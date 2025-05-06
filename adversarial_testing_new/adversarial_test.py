import yaml
import json
import pandas as pd
import random
import time
import requests
from pathlib import Path
from attacks.transformations import StringTransformation
from attacks.templates import ATTACK_TEMPLATES, TRANSFORMATION_METHODS

class AdversarialTester:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.test_cases = self._load_test_cases()
        self.transformer = StringTransformation()
        self.results = []
        
        # Your Gemini API configuration
        self.gemini_url = "https://your-gemini-endpoint.com/v3/session:detectIntent"
        self.gemini_headers = {
            "Authorization": "Bearer YOUR_ACCESS_TOKEN",
            "Content-Type": "application/json"
        }

    def _load_config(self, path: str) -> dict:
        with open(path) as f:
            return yaml.safe_load(f)
        
    def _load_test_cases(self) -> dict:
        with open(Path("data") / "test_cases.json") as f:
            return json.load(f)


    def generate_attacks(self) -> list:
    attacks = []
    
    for category, base_queries in self.test_cases.items():
        templates = ATTACK_TEMPLATES.get(category, [])
        
        for base_query in base_queries:
            # 1. Single random template variant
            if templates:
                template = random.choice(templates)
                templated = template.format(query=base_query)
                attacks.append(self._create_record(
                    base=base_query,
                    category=category,
                    transformed=templated,
                    attack_type="template",
                    variant_type=template.split(":")[0].strip()
                ))
            
            # 2. All transformation variants
            for transform in TRANSFORMATION_METHODS:
                transformed = self.transformer.transform(base_query, transform)
                attacks.append(self._create_record(
                    base=base_query,
                    category=category,
                    transformed=transformed,
                    attack_type="transformation",
                    variant_type=transform
                ))
            
            # 3. Single random combined variant (template + random transform)
            if templates:
                template = random.choice(templates)
                transform = random.choice(TRANSFORMATION_METHODS)
                combined = self.transformer.transform(
                    template.format(query=base_query),
                    transform
                )
                attacks.append(self._create_record(
                    base=base_query,
                    category=category,
                    transformed=combined,
                    attack_type="combined",
                    variant_type=f"{template.split(':')[0].strip()}+{transform}"
                ))
    
    return attacks

    
    # def generate_attacks(self) -> list:
    # attacks = []
    # categories = list(self.test_cases.keys())
    # unused_queries = {category: list(queries) for category, queries in self.test_cases.items()}

    # while len(attacks) < self.config['max_total_queries']:
    #     for category in categories:
    #         if not unused_queries[category]:
    #             continue
                
    #         base_query = unused_queries[category].pop(0)
    #         variant_type = random.choice(["template", "transformation", "combined"])
            
    #         if variant_type == "template":
    #             template = random.choice(ATTACK_TEMPLATES.get(category, []))
    #             transformed = template.format(query=base_query)
    #             variant_details = template  # Template name as variant_type
    #         elif variant_type == "transformation":
    #             transform = random.choice(TRANSFORMATION_METHODS)
    #             transformed = self.transformer.transform(base_query, transform)
    #             variant_details = transform  # Transformation method as variant_type
    #         else:  # combined
    #             template = random.choice(ATTACK_TEMPLATES.get(category, []))
    #             transform = random.choice(TRANSFORMATION_METHODS)
    #             transformed = self.transformer.transform(template.format(query=base_query), transform)
    #             variant_details = f"{template}+{transform}"  # Combined details
            
    #         attacks.append(self._create_record(
    #             base_query, category, transformed, 
    #             variant_type, variant_details  # Now includes both attack_type and variant_type
    #         ))
            
    #         if len(attacks) >= self.config['max_total_queries']:
    #             break
    
    # return attacks[:self.config['max_total_queries']]

    # new generate_attacks function:

    # def generate_attacks(self) -> list:
    # attacks = []
    # # Include ALL template categories from templates.py
    # all_template_categories = list(ATTACK_TEMPLATES.keys())
    # categories_with_test_cases = list(self.test_cases.keys())
    
    # # Prepare queries: use test cases where available, else empty list
    # unused_queries = {
    #     category: random.sample(self.test_cases.get(category, []), len(self.test_cases.get(category, [])))
    #     for category in all_template_categories
    # }

    # while len(attacks) < self.config['max_total_queries']:
    #     for category in all_template_categories:
    #         if not unused_queries[category]:
    #             # For template-only categories, borrow a random base query
    #             if category not in categories_with_test_cases:
    #                 donor_category = random.choice(categories_with_test_cases)
    #                 if self.test_cases[donor_category]:
    #                     base_query = random.choice(self.test_cases[donor_category])
    #                 else:
    #                     continue
    #             else:
    #                 continue
    #         else:
    #             base_query = unused_queries[category].pop(0)
            
    #         # Force template attacks for template-only categories
    #         variant_type = "template" if category not in categories_with_test_cases else random.choice(["template", "transformation", "combined"])
            
    #         if variant_type == "template":
    #             template = random.choice(ATTACK_TEMPLATES.get(category, []))
    #             transformed = template.format(query=base_query)
    #             variant_details = template
    #         elif variant_type == "transformation":
    #             transform = random.choice(TRANSFORMATION_METHODS)
    #             transformed = self.transformer.transform(base_query, transform)
    #             variant_details = transform
    #         else:
    #             template = random.choice(ATTACK_TEMPLATES.get(category, []))
    #             transform = random.choice(TRANSFORMATION_METHODS)
    #             transformed = self.transformer.transform(template.format(query=base_query), transform)
    #             variant_details = f"{template}+{transform}"
            
    #         attacks.append(self._create_record(
    #             base_query, category, transformed, 
    #             variant_type, variant_details
    #         ))
            
    #         if len(attacks) >= self.config['max_total_queries']:
    #             break
    
    # return attacks[:self.config['max_total_queries']]
    
    # def _generate_variants(self, base_query: str, category: str) -> list:
    #     """Generate variants for a single base query"""
    #     variants = []
        
    #     # Template-based attacks
    #     templates = ATTACK_TEMPLATES.get(category, []) + \
    #                ATTACK_TEMPLATES.get("prompt_injection", []) + \
    #                ATTACK_TEMPLATES.get("role_play", [])
        
    #     for template in random.sample(templates, min(len(templates), self.config['variants_per_template'])):
    #         transformed = template.format(query=base_query)
    #         variants.append(self._create_record(base_query, category, transformed, "template", template))
            
    #     # Transformation attacks
    #     transforms = random.sample(
    #         TRANSFORMATION_METHODS, 
    #         min(len(TRANSFORMATION_METHODS), self.config['variants_per_transformation'])
    #     )
        
    #     for transform in transforms:
    #         transformed = self.transformer.transform(base_query, transform)
    #         variants.append(self._create_record(base_query, category, transformed, "transformation", transform))
            
    #     # Combined attacks
    #     for _ in range(self.config['variants_combined']):
    #         template = random.choice(templates)
    #         transform = random.choice(TRANSFORMATION_METHODS)
    #         transformed = self.transformer.transform(
    #             template.format(query=base_query), 
    #             transform
    #         )
    #         variants.append(self._create_record(
    #             base_query, category, transformed, 
    #             "combined", f"{template}+{transform}"
    #         ))
            
    #     return variants
    
    def _create_record(self, base: str, category: str, transformed: str, 
                      attack_type: str, variant: str = "") -> dict:
        """Create result record structure"""
        return {
            "base_query": base,
            "category": category,
            "transformed_query": transformed,
            "attack_type": attack_type,
            "variant_type": variant,
            "response": "",
            "timestamp": pd.Timestamp.now().isoformat()
        }
    
    def execute_attacks(self, attacks: list):
        """Execute all generated attacks"""
        for idx, attack in enumerate(attacks):
            try:
                response = self._query_gemini(attack['transformed_query'])
                self.results.append({**attack, "response": response})
                
                if (idx + 1) % 10 == 0:
                    print(f"Processed {idx + 1}/{len(attacks)} queries")
                
                time.sleep(self.config['rate_limit'])
                
            except Exception as e:
                print(f"Error processing query {idx + 1}: {str(e)}")
                self.results.append({**attack, "response": f"ERROR: {str(e)}"})
    
    def _query_gemini(self, query: str) -> str:
        """Your exact query_gemini implementation"""
        data = {
            "queryInput": {
                "text": {
                    "text": query,
                    "languageCode": "en-US"
                }
            }
        }
        
        try:
            response = requests.post(
                self.gemini_url,
                headers=self.gemini_headers,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if ('queryResult' in result and 
                'responseMessages' in result['queryResult'] and 
                result['queryResult']['responseMessages']):
                if ('text' in result['queryResult']['responseMessages'][0] and 
                    'text' in result['queryResult']['responseMessages'][0]['text'] and 
                    result['queryResult']['responseMessages'][0]['text']['text']):
                    return result['queryResult']['responseMessages'][0]['text']['text'][0]
                return "No text response found."
            return "Unexpected response format."
            
        except requests.exceptions.RequestException as e:
            print(f"Error during detectIntent request: {e}")
            if response is not None:
                print(f"Status Code: {response.status_code}")
                print(f"Response Body: {response.text}")
            return None
    
    def save_results(self):
        """Save results to Excel with analysis"""
        df = pd.DataFrame(self.results)
        
        with pd.ExcelWriter(self.config['output_file']) as writer:
            # Save main results
            df.to_excel(writer, sheet_name='Results', index=False)
            
            # Attack distribution
            attack_dist = df['attack_type'].value_counts(normalize=True).mul(100).round(1)
            attack_dist.to_excel(writer, sheet_name='Attack Distribution')
            
            # Vulnerability coverage
            vuln_coverage = df['category'].value_counts(normalize=True).mul(100).round(1)
            vuln_coverage.to_excel(writer, sheet_name='Vulnerability Coverage')
        
        print(f"Results saved to {self.config['output_file']}")

def main():
    print("Starting adversarial testing...")
    
    tester = AdversarialTester()
    
    # Generate attacks
    print("Generating adversarial queries...")
    attacks = tester.generate_attacks()
    print(f"Generated {len(attacks)} adversarial queries")
    
    # Execute attacks
    print("Executing attacks against Gemini...")
    tester.execute_attacks(attacks)
    
    # Save results
    print("Saving results...")
    tester.save_results()
    
    print("Adversarial testing complete!")

if __name__ == "__main__":
    main()
