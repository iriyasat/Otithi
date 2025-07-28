# Otithi CSS Architecture

This directory contains the modular CSS architecture for the Otithi application. The styles are organized into logical modules while maintaining the same theme and visual consistency.

## File Structure

### Core Files
- **`style.css`** - Main stylesheet that imports all other CSS files
- **`variables.css`** - Design tokens, colors, typography, spacing, and other CSS custom properties
- **`base.css`** - Reset styles, typography, and global base styles
- **`layout.css`** - Grid systems, layout utilities, and structural components
- **`components.css`** - Reusable UI components (buttons, forms, cards, badges, etc.)
- **`navigation.css`** - Navigation bar, footer, and navigation-related components
- **`animations.css`** - All animations, transitions, and keyframes
- **`utilities.css`** - Utility classes and helper functions

### Page-Specific Files
- **`auth.css`** - Authentication pages (login, register)
- **`home.css`** - Homepage and landing page styles
- **`dashboard.css`** - Dashboard pages (admin, host, guest)
- **`profile.css`** - User profile and settings pages
- **`responsive.css`** - Responsive design breakpoints and mobile-specific styles

## Import Order

The main `style.css` file imports CSS files in the following order:

1. **Variables** - Design tokens and custom properties
2. **Base** - Reset and typography
3. **Layout** - Grid systems and structural components
4. **Components** - Reusable UI components
5. **Navigation** - Navigation and footer
6. **Animations** - All animations and transitions
7. **Utilities** - Helper classes
8. **Page-specific** - Individual page styles
9. **Responsive** - Mobile and responsive styles

## Design System

### Colors
- **Primary**: Green theme (`--primary-500: #006a4e`)
- **Neutral**: Gray scale for text and backgrounds
- **Accent**: Coral, blue, and purple for special elements

### Typography
- **Font Family**: Inter (Google Fonts)
- **Font Weights**: 300, 400, 500, 600, 700, 800
- **Font Sizes**: xs, sm, base, lg, xl, 2xl, 3xl, 4xl, 5xl, 6xl

### Spacing
- **Space Scale**: 1 (4px) to 32 (128px)
- **Consistent spacing** using CSS custom properties

### Border Radius
- **Scale**: sm, base, md, lg, xl, 2xl, full
- **Consistent rounded corners** throughout the application

### Shadows
- **Scale**: xs, sm, base, md, lg, xl
- **Layered shadows** for depth and elevation

## Usage

### Adding New Styles

1. **Components**: Add reusable components to `components.css`
2. **Page-specific**: Add page-specific styles to the appropriate file (e.g., `dashboard.css`)
3. **Utilities**: Add utility classes to `utilities.css`
4. **Animations**: Add animations to `animations.css`

### Best Practices

1. **Use CSS Custom Properties**: Always use variables from `variables.css`
2. **Mobile First**: Write responsive styles with mobile-first approach
3. **Consistent Naming**: Use BEM methodology for component naming
4. **Performance**: Minimize CSS specificity and avoid deep nesting
5. **Accessibility**: Ensure proper contrast ratios and focus states

### Utility Classes

The `utilities.css` file provides a comprehensive set of utility classes:

- **Spacing**: `m-*`, `p-*`, `mt-*`, `mb-*`, etc.
- **Display**: `d-flex`, `d-grid`, `d-none`, etc.
- **Flexbox**: `justify-content-*`, `align-items-*`, etc.
- **Text**: `text-center`, `font-weight-*`, `font-size-*`, etc.
- **Colors**: `text-primary`, `bg-neutral-100`, etc.
- **Borders**: `border`, `rounded`, `border-primary`, etc.
- **Shadows**: `shadow-sm`, `shadow-md`, `shadow-lg`, etc.

### Animation Classes

The `animations.css` file provides animation utility classes:

- **Fade**: `animate-fade-in`, `animate-fade-in-up`, etc.
- **Slide**: `animate-slide-in-left`, `animate-slide-in-right`, etc.
- **Scale**: `animate-scale-in`, `animate-scale-out`
- **Spin**: `animate-spin`, `animate-spin-slow`
- **Hover**: `animate-hover-lift`, `animate-hover-glow`

## Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest versions)
- **CSS Features**: CSS Grid, Flexbox, CSS Custom Properties, CSS Animations
- **Fallbacks**: Graceful degradation for older browsers

## Performance

- **Modular Loading**: Only load necessary CSS for each page
- **Optimized Selectors**: Efficient CSS selectors for better performance
- **Minified**: CSS files should be minified in production
- **Caching**: Proper cache headers for CSS files

## Maintenance

- **Consistent Updates**: Update design tokens in `variables.css`
- **Component Updates**: Modify components in `components.css`
- **Page Updates**: Update page-specific styles in respective files
- **Testing**: Test across different screen sizes and browsers

## File Sizes

- **Total CSS**: ~150KB (unminified)
- **Core Files**: ~80KB (variables, base, layout, components, navigation, animations, utilities)
- **Page-specific**: ~70KB (auth, home, dashboard, profile, responsive)

## Future Enhancements

- **CSS-in-JS**: Consider CSS-in-JS for dynamic styling
- **CSS Modules**: Implement CSS modules for better scoping
- **PostCSS**: Add PostCSS for advanced CSS processing
- **Design Tokens**: Expand design token system
- **Dark Mode**: Add dark mode support
- **Theming**: Implement multiple theme support 