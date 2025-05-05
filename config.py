import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dictionary containing configuration for different programming languages
LANGUAGE_CONFIGS = {
    'python': {
        'name': 'Python',
        'extensions': ['.py'],
        'single_line_comments': ['#'],
        'multi_line_comments': [('"""', '"""'), ("'''", "'''")],
        'patterns': {
            'import': r'^(?:from\s+\w+\s+)?import\s+\w+',
            'class_definition': r'^\s*class\s+\w+',
            'function_definition': r'^\s*def\s+\w+',
            'variable_declaration': r'^\s*[a-zA-Z_]\w*\s*=',
        }
    },
    'java': {
        'name': 'Java',
        'extensions': ['.java'],
        'single_line_comments': ['//'],
        'multi_line_comments': [('/*', '*/')],
        'patterns': {
            'import': r'^import\s+[\w.]+;?',
            'class_definition': r'^\s*(public|private|protected)?\s*class\s+\w+',
            'function_definition': r'^\s*(public|private|protected|static|\s)*\s*[\w<>\[\]]+\s+\w+\s*\(',
            'variable_declaration': r'^\s*(private|public|protected|static)*\s*[\w<>\[\]]+\s+\w+\s*[=;]',
        }
    },
    'javascript': {
        'name': 'JavaScript',
        'extensions': ['.js'],
        'single_line_comments': ['//'],
        'multi_line_comments': [('/*', '*/')],
        'patterns': {
            'import': r'^import\s+.*from\s+[\'"].*[\'"]',
            'function_definition': r'^\s*(?:function\s+\w+|\w+\s*=\s*function)',
            'variable_declaration': r'^\s*(?:var|let|const)\s+\w+',
            'class_definition': r'^\s*class\s+\w+',
        }
    },
    'c': {
        'name': 'C',
        'extensions': ['.c', '.h'],
        'single_line_comments': ['//'],
        'multi_line_comments': [('/*', '*/')],
        'patterns': {
            'include': r'^#include\s+[<"].*[>"]',
            'function_definition': r'^\w+\s+\w+\s*\(',
            'variable_declaration': r'^\s*\w+\s+\w+\s*=?',
        }
    }
}

# Pre-computed mapping of file extensions to programming languages
EXTENSION_TO_LANGUAGE = {
    '.py': 'python',
    '.java': 'java',
    '.js': 'javascript',
    '.c': 'c',
    '.h': 'c'
}
