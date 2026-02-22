"""AgentLang CLI entry point"""

import sys
import logging
import argparse
from pathlib import Path

from .lexer import tokenize
from .parser import parse
from .interpreter import interpret
from .runtime import Runtime


def setup_logging(level=logging.INFO):
    """Configure logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )


def run_file(filepath: str, verbose: bool = False):
    """Run an AgentLang file"""
    if verbose:
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)
    
    logger = logging.getLogger(__name__)
    
    # Read source file
    path = Path(filepath)
    if not path.exists():
        logger.error(f"File not found: {filepath}")
        sys.exit(1)
    
    source = path.read_text()
    logger.info(f"Running {filepath}")
    
    try:
        # Tokenize
        logger.debug("Tokenizing...")
        tokens = tokenize(source)
        logger.debug(f"Generated {len(tokens)} tokens")
        
        # Parse
        logger.debug("Parsing...")
        ast = parse(tokens)
        logger.debug(f"Parsed {len(ast.statements)} statements")
        
        # Interpret
        logger.debug("Interpreting...")
        runtime = Runtime()
        result = interpret(ast, runtime)
        
        logger.info("Execution complete")
        if result:
            print(f"\nResult: {result}")
        
    except SyntaxError as e:
        logger.error(f"Syntax error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=verbose)
        sys.exit(1)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='AgentLang Interpreter',
        epilog='Example: python -m agentlang script.agent'
    )
    
    parser.add_argument(
        'file',
        help='AgentLang file to execute (.agent)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='AgentLang 0.1.0'
    )
    
    args = parser.parse_args()
    
    run_file(args.file, args.verbose)


if __name__ == '__main__':
    main()
