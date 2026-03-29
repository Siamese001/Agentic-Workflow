#!/usr/bin/env python
"""Diagnose OpenAI API Version Issue"""

import openai

print('='*60)
print('OPENAI API VERSION DIAGNOSTIC')
print('='*60)

print(f'\nOpenAI package version: {openai.__version__}')
print(f'Has ChatCompletion attr: {hasattr(openai, "ChatCompletion")}')
print(f'Has chat attr: {hasattr(openai, "chat")}')
print(f'Can create client: {hasattr(openai, "OpenAI")}')

print('\n' + '='*60)
print('API VERSION ANALYSIS')
print('='*60)

if hasattr(openai, 'ChatCompletion'):
    print('✓ Using OpenAI API v0.x (legacy)')
    print('  Compatible with GPTCache embedding')
else:
    print('✗ Using OpenAI API v1.x (new)')
    print('  GPTCache embedding expects v0.x')
    print('  Breaking change: openai.ChatCompletion → openai.OpenAI().chat.completions')

print('\n' + '='*60)
