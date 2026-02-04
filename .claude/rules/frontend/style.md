# Frontend Style

## TypeScript

- Strict mode enabled
- Use `interface` for object shapes, `type` for unions/aliases
- Explicit return types on exported functions
- Prefer `unknown` over `any`
- Use barrel exports (`index.ts`) for public APIs

## React

- Functional components only (no class components)
- Props interfaces named `{Component}Props`
- Destructure props in function signature
- Hooks at top of component, before any conditionals
- Custom hooks prefixed with `use`

## Component Organization

```typescript
// 1. Imports (external, then internal)
import { useState } from 'react';
import { useApi } from '../contexts';

// 2. Types/interfaces
interface MyComponentProps {
  title: string;
  onSubmit: (value: string) => void;
}

// 3. Component
export function MyComponent({ title, onSubmit }: MyComponentProps) {
  // Hooks first
  const [value, setValue] = useState('');
  const api = useApi();

  // Handlers
  const handleSubmit = () => onSubmit(value);

  // Render
  return <div>...</div>;
}
```

## Tailwind CSS

- Use Tailwind utilities, avoid custom CSS
- Mobile-first responsive: base styles for mobile, `md:` for desktop
- Consistent spacing: stick to Tailwind's spacing scale
- For conditional classes, use template literals or classnames library

## File Naming

- Components: PascalCase (`BinsTable.tsx`)
- Tests: Same name with `.test` suffix (`BinsTable.test.tsx`)
- Utilities: camelCase (`auth.ts`)
- Types: camelCase (`bin.ts`)

## Imports

- Absolute imports from `src/` (configured in tsconfig)
- Group imports: external packages, then internal modules
- Use barrel exports for cleaner imports

## Error Handling

- API errors throw `ApiError` class with status code and message
- Components catch errors and display user-friendly messages
- Use error boundaries for unexpected render errors
