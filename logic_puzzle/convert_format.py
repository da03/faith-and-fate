import json
import re

def format_solution_table(header, rows):
    """Convert table format into the specified string format"""
    formatted_rows = []
    for row in rows:
        # Combine header with row values
        pairs = [f"{h}: {v}" for h, v in zip(header, row)]
        formatted_row = "$ " + " | ".join(pairs) + " |"
        formatted_rows.append(formatted_row)
    return "<newline>".join(formatted_rows)

def format_puzzle_input(puzzle, context, include_extra_rules=False):
    """Extract and format the puzzle input including context"""
    #import pdb; pdb.set_trace()
    context_str = context.replace('This is a logic puzzle. There are 3 houses (numbered 1 on the left, 3 on the right), from the perspective of someone standing across the street from them. Each has a different person in them. They have different characteristics:', '').strip()

    # Context is already a formatted string, just replace newlines
    context_str = context_str.replace('\n', '<newline>')
    
    # Get core rules
    clues = puzzle.get('core_rules', [])
    
    # Optionally add extra rules
    if include_extra_rules:
        clues.extend(puzzle.get('extra_rules', []))
    
    clues_str = '\n'.join(clues)
    
    clues_str = clues_str.replace('\n', '<newline>')
    #clues_str = "<newline>".join(clues)

    
    # Combine context and clues
    return f"{context_str}<newline><newline>Clues:<newline>{clues_str}"

def convert_to_text_format(input_json_path, output_text_path, include_extra_rules=False):
    """Convert JSON reasoning path output to text format"""
    # Read JSON file
    with open(input_json_path, 'r') as f:
        data = json.load(f)
    
    formatted_lines = []
    for entry in data:
        # Format input (context + prompt)
        input_text = format_puzzle_input(
            entry,  # contains core_rules and extra_rules
            entry.get('puzzle_context', ''),
            include_extra_rules
        )
        
        # Format reasoning (chain-of-thought)
        reasoning = entry.get('reasoning', '')
        reasoning = reasoning.replace('The puzzle is solved.', '').strip()
        # Replace newlines with <newline> token
        reasoning = reasoning.replace('\n', '<newline>')
        
        # Format solution
        solution = format_solution_table(
            entry['solution']['table_header'],
            entry['solution']['table_rows']
        )
        
        # Combine all parts
        line = f"{input_text}||{reasoning} #### {solution}"
        formatted_lines.append(line)
    
    # Write output file
    with open(output_text_path, 'w') as f:
        for line in formatted_lines:
            f.write(line + '\n')

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_json', type=str, required=True,
                       help='Path to input JSON file with reasoning paths')
    parser.add_argument('--include_extra_rules', action='store_true',
                       help='Include extra rules in addition to core rules')
    args = parser.parse_args()
    
    convert_to_text_format(args.input_json, args.input_json + '.txt', args.include_extra_rules)

if __name__ == "__main__":
    main()
