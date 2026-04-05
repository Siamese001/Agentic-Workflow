from pathlib import Path

# Read current shim template and add deprecation
compat_dir = Path('agentic_core/adg/_compat')
shim_files = list(compat_dir.glob('*.py'))

for f in shim_files[:5]:  # Test on first 5
    content = f.read_text()

    # Add deprecation warning after the docstring
    new_content = content.replace(
        '"""Shim: re-exports from canonical location for backward compatibility."""',
        '"""Shim: re-exports from canonical location for backward compatibility.\n\nDEPRECATED: Import from canonical location directly. This shim will be removed in 90 days.\n"""\n\nimport warnings as _warnings\n_warnings.warn("Import from agentic_core.adg._compat is deprecated, use canonical location", DeprecationWarning, stacklevel=2)'
    )

    f.write_text(new_content)
    print(f'Updated: {f.name}')

print(f'\nUpdated 5 sample files')
