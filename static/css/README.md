# Client Magic CSS Structure

This directory contains the CSS files for the Client Magic application. The CSS has been organized into modular files to improve maintainability and reduce duplication.

## File Structure

- `base.css` - Contains CSS variables, common utility classes, and basic styling
- `colors.css` - Contains color-specific utility classes
- `forms.css` - Contains styles for forms and form elements
- `modals.css` - Contains styles for modals and dialogs
- `tables.css` - Contains styles for tables and data display

## Usage

All CSS files are included in the base template (`templates/base.html`), so they are available throughout the application. The files are loaded in the following order:

1. `base.css` - Loaded first to establish variables and common styles
2. `colors.css` - Loaded next to provide color utility classes
3. `forms.css` - Loaded to style form elements
4. `modals.css` - Loaded to style modal dialogs
5. `tables.css` - Loaded to style tables and data displays

## CSS Variables

CSS variables are defined in `base.css` and are used throughout the other CSS files. This allows for consistent styling and easy theme changes. The main variable categories are:

- Primary Colors (forest-green variants)
- Accent Colors (gold variants)
- Text Colors
- UI Colors (success, warning, danger, info)
- Gray Scale

Example usage:

```css
.my-element {
  background-color: var(--forest-green);
  color: var(--text-on-green);
}
```

## Utility Classes

Utility classes are provided for common styling needs:

- Color utilities (in `colors.css`): `.bg-forest-green`, `.text-gold`, etc.
- Button styles (in `base.css`): `.btn`, `.btn-primary`, etc.
- Form styles (in `forms.css`): `.form-input`, `.form-label`, etc.
- Modal styles (in `modals.css`): `.modal-container`, `.modal-header`, etc.
- Table styles (in `tables.css`): `.table`, `.table-header`, etc.

## Responsive Design

Media queries are used to ensure the application is responsive across different screen sizes. The main breakpoint is at 640px (mobile devices).

## Extending

To add new styles:

1. Determine which file is most appropriate for your styles
2. Add your styles to the appropriate file
3. If creating a new category of styles, consider creating a new file

## Best Practices

1. Use CSS variables for colors and spacing
2. Keep selectors simple and specific
3. Group related styles together
4. Comment your code, especially for complex selectors
5. Use consistent naming conventions 