# Template Structure

This directory contains the templates for the Client Magic application. The templates have been refactored to use a component-based approach for better maintainability and reusability.

## Directory Structure

- `base.html` - The base template that all other templates extend
- `dashboard.html` - The original dashboard template
- `dashboard_refactored.html` - The refactored dashboard template using components
- `index.html` - The landing page template

### Components

Components are reusable HTML snippets that can be included in multiple templates:

- `components/dashboard_styles.html` - CSS styles for the dashboard
- `components/notifications.html` - Success and error notification messages
- `components/action_buttons.html` - Action buttons for the dashboard
- `components/search_bar.html` - Search bar for filtering contacts
- `components/contacts_table.html` - Table displaying contacts
- `components/contact_detail_modal.html` - Modal for viewing and editing contact details

### Macros

Macros are reusable template functions that generate HTML:

- `macros/form_macros.html` - Macros for generating form elements

## Usage

### Including Components

To include a component in a template:

```jinja
{% include "components/component_name.html" %}
```

### Using Macros

To use macros in a template:

```jinja
{% from "macros/macro_file.html" import macro_name %}
{{ macro_name(param1, param2) }}
```

Or import all macros from a file:

```jinja
{% import "macros/macro_file.html" as forms %}
{{ forms.input_field("name", "Name") }}
```

## Benefits of Component-Based Approach

1. **Maintainability**: Smaller, focused components are easier to maintain
2. **Reusability**: Components can be reused across multiple templates
3. **Readability**: Templates are more readable with clear component boundaries
4. **Collaboration**: Multiple developers can work on different components simultaneously
5. **Testing**: Components can be tested in isolation

## Migration Guide

To migrate from the original templates to the component-based approach:

1. Replace sections of the original templates with component includes
2. Use macros for repetitive HTML patterns
3. Keep JavaScript that interacts with components in the main template file

Example:

```jinja
<!-- Original -->
<div class="search-bar">
  <!-- Search bar HTML -->
</div>

<!-- Refactored -->
{% include "components/search_bar.html" %}
``` 