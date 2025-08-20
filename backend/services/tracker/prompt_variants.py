"""
Prompt variant generator for testing different query formulations
Based on technical specification - generates 50-100 prompt variants per cluster
"""

import re
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class VariationType(Enum):
    SYNONYM = "synonym"
    REORDER = "reorder"
    QUESTION_FORMAT = "question_format"
    LONG_TAIL = "long_tail"
    CONVERSATIONAL = "conversational"
    FORMAL = "formal"


@dataclass
class PromptVariant:
    """Individual prompt variant with metadata"""
    text: str
    variant_type: VariationType
    confidence: float  # How likely this variant is to be used
    generation_params: Dict[str, Any]


class PromptVariantGenerator:
    """Generates multiple variations of a seed prompt for testing"""
    
    def __init__(self):
        # Common synonyms for SEO queries
        self.synonyms = {
            "best": ["top", "finest", "leading", "premier", "excellent", "optimal"],
            "good": ["great", "quality", "excellent", "superior", "reliable"],
            "how": ["what is the way to", "what's the method for", "how do you"],
            "what": ["which", "what are", "what is"],
            "why": ["what makes", "what causes", "how come"],
            "company": ["business", "organization", "firm", "enterprise"],
            "service": ["solution", "offering", "platform", "tool"],
            "software": ["platform", "tool", "application", "system"],
            "agency": ["company", "firm", "consultancy", "service provider"],
        }
        
        # Question starters for reformatting
        self.question_starters = [
            "What are the",
            "Which are the",
            "Who are the",
            "How do I find",
            "Where can I find",
            "What makes",
            "Why should I choose",
            "How do I select",
        ]
        
        # Conversational prefixes
        self.conversational_prefixes = [
            "I'm looking for",
            "Can you help me find",
            "I need to know about",
            "Tell me about",
            "I want to understand",
            "Please explain",
            "Help me with",
        ]
    
    def generate_variants(
        self, 
        seed_prompt: str, 
        target_count: int = 75,
        locale: str = "en"
    ) -> List[PromptVariant]:
        """Generate multiple variants of a seed prompt"""
        
        variants = []
        seed_lower = seed_prompt.lower()
        
        # Always include the original
        variants.append(PromptVariant(
            text=seed_prompt,
            variant_type=VariationType.SYNONYM,
            confidence=1.0,
            generation_params={"original": True}
        ))
        
        # Generate different types of variants
        variants.extend(self._generate_synonym_variants(seed_prompt, target_count // 4))
        variants.extend(self._generate_reorder_variants(seed_prompt, target_count // 6))
        variants.extend(self._generate_question_variants(seed_prompt, target_count // 4))
        variants.extend(self._generate_long_tail_variants(seed_prompt, target_count // 5))
        variants.extend(self._generate_conversational_variants(seed_prompt, target_count // 6))
        variants.extend(self._generate_formal_variants(seed_prompt, target_count // 8))
        
        # Remove duplicates and limit to target count
        unique_variants = self._deduplicate_variants(variants)
        
        # If we need more variants, generate additional ones
        while len(unique_variants) < target_count:
            additional = self._generate_creative_variants(seed_prompt, target_count - len(unique_variants))
            unique_variants.extend(additional)
            unique_variants = self._deduplicate_variants(unique_variants)
            break  # Prevent infinite loop
        
        return unique_variants[:target_count]
    
    def _generate_synonym_variants(self, seed: str, count: int) -> List[PromptVariant]:
        """Replace words with synonyms"""
        variants = []
        words = seed.lower().split()
        
        for _ in range(count):
            new_words = words.copy()
            replacements_made = 0
            
            for i, word in enumerate(words):
                if word in self.synonyms and random.random() < 0.4:  # 40% chance to replace
                    new_words[i] = random.choice(self.synonyms[word])
                    replacements_made += 1
            
            if replacements_made > 0:
                new_text = " ".join(new_words)
                variants.append(PromptVariant(
                    text=new_text.capitalize(),
                    variant_type=VariationType.SYNONYM,
                    confidence=0.8,
                    generation_params={"replacements": replacements_made}
                ))
        
        return variants
    
    def _generate_reorder_variants(self, seed: str, count: int) -> List[PromptVariant]:
        """Reorder words while maintaining meaning"""
        variants = []
        words = seed.split()
        
        if len(words) < 3:
            return variants
        
        for _ in range(count):
            # Simple reordering strategies
            reordered = words.copy()
            
            # Strategy 1: Move adjectives
            if len(words) >= 3:
                # Find adjective-noun pairs and potentially swap
                for i in range(len(words) - 1):
                    if random.random() < 0.3:
                        reordered[i], reordered[i + 1] = reordered[i + 1], reordered[i]
            
            new_text = " ".join(reordered)
            if new_text != seed:
                variants.append(PromptVariant(
                    text=new_text,
                    variant_type=VariationType.REORDER,
                    confidence=0.7,
                    generation_params={"strategy": "word_swap"}
                ))
        
        return variants
    
    def _generate_question_variants(self, seed: str, count: int) -> List[PromptVariant]:
        """Convert statements to questions"""
        variants = []
        
        for starter in self.question_starters[:count]:
            # Simple question formation
            if "best" in seed.lower():
                question = f"{starter} {seed.lower().replace('best ', '')}"
            elif "how to" in seed.lower():
                question = seed  # Already a question
            else:
                question = f"{starter} {seed.lower()}"
            
            question = question.capitalize().rstrip('.') + "?"
            
            variants.append(PromptVariant(
                text=question,
                variant_type=VariationType.QUESTION_FORMAT,
                confidence=0.85,
                generation_params={"starter": starter}
            ))
        
        return variants
    
    def _generate_long_tail_variants(self, seed: str, count: int) -> List[PromptVariant]:
        """Generate longer, more specific variants"""
        variants = []
        
        # Common modifiers for long-tail
        modifiers = [
            "for small business",
            "in 2024",
            "for startups",
            "with pricing",
            "with reviews",
            "comparison",
            "that integrates with",
            "for agencies",
            "with free trial",
            "for enterprise"
        ]
        
        for i in range(count):
            modifier = modifiers[i % len(modifiers)]
            long_tail = f"{seed} {modifier}"
            
            variants.append(PromptVariant(
                text=long_tail,
                variant_type=VariationType.LONG_TAIL,
                confidence=0.75,
                generation_params={"modifier": modifier}
            ))
        
        return variants
    
    def _generate_conversational_variants(self, seed: str, count: int) -> List[PromptVariant]:
        """Generate conversational style prompts"""
        variants = []
        
        for prefix in self.conversational_prefixes[:count]:
            conversational = f"{prefix} {seed.lower()}"
            
            variants.append(PromptVariant(
                text=conversational.capitalize(),
                variant_type=VariationType.CONVERSATIONAL,
                confidence=0.8,
                generation_params={"prefix": prefix}
            ))
        
        return variants
    
    def _generate_formal_variants(self, seed: str, count: int) -> List[PromptVariant]:
        """Generate formal/academic style variants"""
        variants = []
        
        formal_patterns = [
            f"An analysis of {seed.lower()}",
            f"Comprehensive guide to {seed.lower()}",
            f"Professional assessment of {seed.lower()}",
            f"Enterprise solutions for {seed.lower()}",
            f"Industry standards for {seed.lower()}",
        ]
        
        for pattern in formal_patterns[:count]:
            variants.append(PromptVariant(
                text=pattern,
                variant_type=VariationType.FORMAL,
                confidence=0.7,
                generation_params={"pattern": "formal"}
            ))
        
        return variants
    
    def _generate_creative_variants(self, seed: str, count: int) -> List[PromptVariant]:
        """Generate additional creative variants when needed"""
        variants = []
        
        creative_modifications = [
            f"{seed} recommendations",
            f"{seed} options",
            f"{seed} alternatives",
            f"Top {seed.lower()} solutions",
            f"Ultimate {seed.lower()} guide",
        ]
        
        for mod in creative_modifications[:count]:
            variants.append(PromptVariant(
                text=mod,
                variant_type=VariationType.SYNONYM,
                confidence=0.6,
                generation_params={"creative": True}
            ))
        
        return variants
    
    def _deduplicate_variants(self, variants: List[PromptVariant]) -> List[PromptVariant]:
        """Remove duplicate variants based on text"""
        seen = set()
        unique = []
        
        for variant in variants:
            text_lower = variant.text.lower().strip()
            if text_lower not in seen:
                seen.add(text_lower)
                unique.append(variant)
        
        return unique
    
    def analyze_variant_distribution(self, variants: List[PromptVariant]) -> Dict[str, int]:
        """Analyze the distribution of variant types"""
        distribution = {}
        for variant in variants:
            variant_type = variant.variant_type.value
            distribution[variant_type] = distribution.get(variant_type, 0) + 1
        return distribution


# Utility functions
def generate_prompt_variants(seed: str, count: int = 75, locale: str = "en") -> List[PromptVariant]:
    """Convenience function to generate prompt variants"""
    generator = PromptVariantGenerator()
    return generator.generate_variants(seed, count, locale)


def variants_to_strings(variants: List[PromptVariant]) -> List[str]:
    """Convert variants to simple string list"""
    return [variant.text for variant in variants]