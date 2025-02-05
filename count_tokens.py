from transformers import AutoTokenizer
import numpy as np
import argparse

def get_percentile_stats(values):
    """Calculate various percentile statistics for a list of values"""
    return {
        'median': np.percentile(values, 50),
        '85%': np.percentile(values, 85),
        '90%': np.percentile(values, 90),
        '95%': np.percentile(values, 95),
        '97%': np.percentile(values, 97),
        '99%': np.percentile(values, 99),
        'max': max(values),
        'mean': np.mean(values)
    }

def analyze_token_counts(input_file):
    """Analyze token counts for input, reasoning, and output sections"""
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    input_tokens = []
    reasoning_tokens = []
    output_tokens = []
    total_tokens = []
    
    with open(input_file, 'r') as f:
        for line in f:
            # Split into sections
            input_text, rest = line.split('||')
            reasoning, output = rest.split(' #### ')
            
            # Count tokens for each section
            input_count = len(tokenizer.encode(input_text))
            reasoning_count = len(tokenizer.encode(reasoning))
            output_count = len(tokenizer.encode(output))
            
            input_tokens.append(input_count)
            reasoning_tokens.append(reasoning_count)
            output_tokens.append(output_count)
            total_tokens.append(input_count + reasoning_count + output_count)
    
    # Calculate statistics for each section
    stats = {
        'input': get_percentile_stats(input_tokens),
        'reasoning': get_percentile_stats(reasoning_tokens),
        'output': get_percentile_stats(output_tokens),
        'total': get_percentile_stats(total_tokens)
    }
    
    # Print results
    print("\nToken count statistics:")
    for section in ['input', 'reasoning', 'output', 'total']:
        print(f"\n{section.upper()}:")
        for metric, value in stats[section].items():
            print(f"{metric}: {value:.1f}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, required=True,
                       help='Path to input text file with formatted examples')
    args = parser.parse_args()
    
    analyze_token_counts(args.input_file)

if __name__ == "__main__":
    main()
