"""
Prompt Taxonomy

Template taxonomy with 10 prompt categories, category loaders,
and registry for prompt assembly.
"""

from .categories import (
    CategoryRegistryEntry,
    CategoryTemplate,
    PromptCategory,
    PromptCategoryRegistry,
    get_default_template_path,
)
from .loader import (
    TemplateLoader,
    TemplateLoaderFactory,
    TemplateLoadError,
)
from .template_manifest import (
    ExtendedTemplateManifest,
    TemplateManifestRegistry,
)

__all__ = [
    # Categories
    "PromptCategory",
    "CategoryTemplate",
    "CategoryRegistryEntry",
    "PromptCategoryRegistry",
    "get_default_template_path",
    # Template manifest
    "ExtendedTemplateManifest",
    "TemplateManifestRegistry",
    # Loader
    "TemplateLoader",
    "TemplateLoadError",
    "TemplateLoaderFactory",
]
