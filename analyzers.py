from typing import Dict, Any, Generator
import os
import mmap
import re
from collections import defaultdict
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from config import logger, LANGUAGE_CONFIGS, EXTENSION_TO_LANGUAGE

class ChunkProcessor:
    """Handles the processing of large file chunks"""
    
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks
    
    @staticmethod
    def get_file_chunks(file_path: str, chunk_size: int = CHUNK_SIZE) -> Generator[str, None, None]:
        """Generator that yields chunks of a file"""
        try:
            with open(file_path, 'rb') as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    buffer = ""
                    total_size = mm.size()
                    processed = 0
                    
                    while processed < total_size:
                        chunk = mm.read(chunk_size)
                        processed += len(chunk)
                        
                        if not chunk:
                            break
                            
                        text = chunk.decode('utf-8', errors='replace')
                        lines = (buffer + text).split('\n')
                        
                        if text:
                            buffer = lines[-1]
                            lines = lines[:-1]
                        
                        for line in lines:
                            yield line + '\n'
                    
                    if buffer:
                        yield buffer
        except Exception as e:
            logger.error(f"Error reading file chunks: {str(e)}")
            raise

class FileProcessor:
    """Handles file size checks and processing decisions"""
    
    LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def is_large_file(file_path: str) -> bool:
        """Check if file should be processed as a large file"""
        try:
            return os.path.getsize(file_path) > FileProcessor.LARGE_FILE_THRESHOLD
        except OSError:
            return False

    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except OSError:
            return 0.0

class LineClassifier:
    """Helper class to classify different types of code lines"""
    
    def __init__(self, language_config: Dict[str, Any]):
        self.patterns = {
            category: re.compile(pattern)
            for category, pattern in language_config.get('patterns', {}).items()
        }
    
    def classify_line(self, line: str) -> str:
        for category, pattern in self.patterns.items():
            if pattern.match(line):
                return category
        return 'other_code'

class LineCounter:
    """Counts and categorizes lines in source code files"""
    
    def __init__(self, language_config: Dict[str, Any]):
        self.config = language_config
        self.classifier = LineClassifier(language_config)
        self.chunk_processor = ChunkProcessor()
        self.reset_counters()

    def reset_counters(self) -> None:
        self.stats = {
            'blank': 0,
            'comments': 0,
            'code': 0,
            'total': 0,
            'detailed': defaultdict(int)
        }
        self.in_multi_line_comment = False
        self.current_multi_line_comment = None

    def is_blank_line(self, line: str) -> bool:
        return not line.strip()

    def is_single_line_comment(self, line: str) -> bool:
        stripped_line = line.strip()
        return any(stripped_line.startswith(comment) 
                  for comment in self.config['single_line_comments'])

    def check_multi_line_comment(self, line: str) -> bool:
        if not self.in_multi_line_comment:
            for start, end in self.config['multi_line_comments']:
                if start in line:
                    if end in line[line.index(start) + len(start):]:
                        return len(line[:line.index(start)].strip()) == 0
                    self.in_multi_line_comment = True
                    self.current_multi_line_comment = (start, end)
                    return True
        else:
            if self.current_multi_line_comment[1] in line:
                self.in_multi_line_comment = False
                self.current_multi_line_comment = None
            return True
        return False

    def process_line(self, line: str) -> None:
        """
        Process a single line and update counters.
        Code lines include everything except blanks and comments.
        """
        if self.is_blank_line(line):
            self.stats['blank'] += 1
            self.stats['detailed']['blank'] += 1
        elif self.is_single_line_comment(line) or self.check_multi_line_comment(line):
            self.stats['comments'] += 1
            self.stats['detailed']['comments'] += 1
        else:
            # This is a code line - classify it for detailed stats
            self.stats['code'] += 1  # Increment total code counter
            
            # Also classify it into specific categories for detailed breakdown
            matched = False
            for category, pattern in self.classifier.patterns.items():
                if pattern.match(line):
                    self.stats['detailed'][category] += 1
                    matched = True
                    break
            
            # If no specific pattern matched, it's still code
            if not matched:
                self.stats['detailed']['other_code'] += 1
        
        self.stats['total'] += 1

    def count_lines(self, filename: str) -> Dict[str, int]:
        """Enhanced line counting with large file support"""
        try:
            self.reset_counters()
            file_size_mb = FileProcessor.get_file_size_mb(filename)
            
            logger.info(f"Processing file: {filename} ({file_size_mb:.2f} MB)")
            
            if FileProcessor.is_large_file(filename):
                logger.info(f"Using chunk processing for large file: {filename}")
                for line in self.chunk_processor.get_file_chunks(filename):
                    self.process_line(line)
            else:
                with open(filename, 'r', encoding='utf-8') as file:
                    for line in file:
                        self.process_line(line)
                        
            return self.stats
                
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            return None

class SourceTreeAnalyzer:
    """Analyzes entire directory trees with parallel processing support"""
    
    def __init__(self):
        self.file_count = defaultdict(int)
        self.file_details = defaultdict(list)
        self.total_stats = defaultdict(lambda: {
            'blank': 0,
            'comments': 0,
            'code': 0,
            'total': 0,
            'detailed': defaultdict(int)
        })
        self.max_workers = os.cpu_count() or 1

    def analyze_directory(self, directory: str) -> Dict:
        directory_path = Path(directory)
        files_to_process = []
        total_size = 0
        
        # Collect files and calculate total size
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in EXTENSION_TO_LANGUAGE:
                files_to_process.append(str(file_path))
                total_size += os.path.getsize(file_path)
        
        logger.info(f"Found {len(files_to_process)} files to process "
                   f"(Total size: {total_size / (1024*1024):.2f} MB)")
        
        # Process files in parallel with size-based batching
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for file_path in files_to_process:
                if FileProcessor.is_large_file(file_path):
                    futures.append(executor.submit(process_file, file_path))
                else:
                    futures.append(executor.submit(process_file, file_path))
            
            # Process results as they complete
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        self.update_totals(result)
                        self.file_details[result['language']].append(result)
                except Exception as e:
                    logger.error(f"Error processing file: {str(e)}")
        
        return self.get_summary()

    def update_totals(self, result: Dict) -> None:
        language = result['language']
        self.file_count[language] += 1
        
        # Update main statistics
        self.total_stats[language]['blank'] += result['stats']['blank']
        self.total_stats[language]['comments'] += result['stats']['comments']
        self.total_stats[language]['code'] += result['stats']['code']
        self.total_stats[language]['total'] += result['stats']['total']
        
        # Update detailed statistics
        for category, count in result['stats']['detailed'].items():
            self.total_stats[language]['detailed'][category] += count

    def get_summary(self) -> Dict:
        return {
            'by_language': {
                language: {
                    'file_count': self.file_count[language],
                    'statistics': {
                        'blank': self.total_stats[language]['blank'],
                        'comments': self.total_stats[language]['comments'],
                        'code': self.total_stats[language]['code'],
                        'total': self.total_stats[language]['total'],
                        'detailed': dict(self.total_stats[language]['detailed'])
                    },
                    'files': sorted(
                        self.file_details[language],
                        key=lambda x: os.path.getsize(x['filename']),
                        reverse=True
                    )
                }
                for language, _ in self.file_count.items()
            },
            'total_files': sum(self.file_count.values())
        }


def process_file(filename: str) -> Dict[str, Any]:
    """Process a single file with enhanced error handling"""
    try:
        ext = os.path.splitext(filename)[1].lower()
        language_id = EXTENSION_TO_LANGUAGE.get(ext)

        if not language_id:
            logger.warning(f"Unsupported file type for {filename}")
            return None

        language_config = LANGUAGE_CONFIGS[language_id]
        counter = LineCounter(language_config)
        results = counter.count_lines(filename)
        
        if results:
            return {
                'filename': filename,
                'language': language_config['name'],
                'stats': results
            }
    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}")
    return None
