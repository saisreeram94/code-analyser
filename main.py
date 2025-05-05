from typing import Dict, Any, List
import time
import os
from pathlib import Path
from config import logger, EXTENSION_TO_LANGUAGE
from analyzers import process_file, SourceTreeAnalyzer, FileProcessor

def format_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def print_detailed_results(summary: Dict):
    """Print detailed analysis results"""
    print("\nSource Tree Analysis Summary")
    print("=" * 80)
    
    print(f"Total Files Analyzed: {summary['total_files']}")
    total_size = 0
    
    # Main categories to always display first
    main_categories = ['blank', 'comments', 'code']
    
    # Detailed code breakdown categories
    code_breakdown_categories = [
        'import',
        'class_definition',
        'function_definition',
        'variable_declaration',
        'other_code'
    ]
    
    for language, data in summary['by_language'].items():
        print(f"\n{language} Summary:")
        print("=" * 40)
        print(f"Total Files: {data['file_count']}")
        
        # Print language-level statistics
        print("\nLanguage-wide Statistics:")
        print("-" * 30)
        
        # Print main categories first
        stats = data['statistics']
        for category in main_categories:
            count = stats.get(category, 0)
            print(f"{category.replace('_', ' ').title()}: {count}")
        
        # Print code breakdown
        print("\nCode Breakdown:")
        print("-" * 20)
        for category in code_breakdown_categories:
            count = stats['detailed'].get(category, 0)
            print(f"{category.replace('_', ' ').title()}: {count}")
        
        # Print individual file statistics
        print(f"\nIndividual File Details for {language}:")
        print("-" * 60)
        
        for file_data in data['files']:
            file_size = os.path.getsize(file_data['filename'])
            total_size += file_size
            
            print(f"\nFile: {os.path.basename(file_data['filename'])}")
            print(f"Path: {file_data['filename']}")
            print(f"Size: {format_size(file_size)}")
            
            # Print main categories
            for category in main_categories:
                count = file_data['stats'].get(category, 0)
                print(f"  {category.replace('_', ' ').title()}: {count}")
            
            # Print code breakdown
            print("  Code Breakdown:")
            for category in code_breakdown_categories:
                count = file_data['stats']['detailed'].get(category, 0)
                print(f"    {category.replace('_', ' ').title()}: {count}")
            
            print(f"  Total Lines: {file_data['stats']['total']}")
            print("-" * 30)
    
    print(f"\nTotal Size Processed: {format_size(total_size)}")

def main():
    """Enhanced main program with better resource handling"""
    while True:
        print("\nEnter path to analyze (file or directory) or 'quit' to exit:")
        user_input = input("Path: ").strip()
        
        if user_input.lower() in ('quit', 'exit'):
            break
        
        path = Path(user_input)
        start_time = time.time()
        
        try:
            if path.is_file():
                file_size = os.path.getsize(path)
                logger.info(f"Processing single file ({format_size(file_size)})")
                
                result = process_file(str(path))
                if result:
                    print_detailed_results({
                        'total_files': 1,
                        'by_language': {
                            result['language']: {
                                'file_count': 1,
                                'statistics': {
                                    'blank': result['stats']['blank'],
                                    'comments': result['stats']['comments'],
                                    'code': result['stats']['code'],
                                    'detailed': result['stats']['detailed']
                                },
                                'files': [result]
                            }
                        }
                    })
            elif path.is_dir():
                # Count files and total size before processing
                file_count = 0
                total_size = 0
                for file_path in path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in EXTENSION_TO_LANGUAGE:
                        file_count += 1
                        total_size += os.path.getsize(file_path)
                
                logger.info(f"Found {file_count} files to process "
                           f"(Total size: {format_size(total_size)})")
                
                analyzer = SourceTreeAnalyzer()
                summary = analyzer.analyze_directory(str(path))
                print_detailed_results(summary)
            else:
                print("Invalid path!")
                continue
            
            elapsed_time = time.time() - start_time
            print(f"\nAnalysis completed in {elapsed_time:.2f} seconds")
            
        except KeyboardInterrupt:
            print("\nAnalysis interrupted by user.")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
