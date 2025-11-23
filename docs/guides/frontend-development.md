# Frontend Development Guide

**Status:** 🚧 In Progress

## Overview

ProjectGoat's frontend is built with React 18.3.1, TypeScript, Vite, and Radix UI components. This guide covers the frontend architecture, development workflow, and best practices.

## Technology Stack

- **React 18.3.1** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Radix UI** - Headless UI component library
- **shadcn/ui** - Pre-built component collection
- **TailwindCSS** - Utility-first CSS
- **Lucide React** - Icon library
- **React Hook Form** - Form management
- **Recharts** - Data visualization

## Project Structure

```
src/
├── components/
│   ├── ui/              # Reusable UI components (shadcn/ui)
│   ├── *View.tsx        # Main view components
│   └── *Dialog.tsx      # Dialog components
├── services/
│   ├── api.ts           # API client configuration
│   ├── auth.ts          # Authentication service
│   ├── tasks.ts         # Task API calls
│   ├── projects.ts      # Project API calls
│   └── ... (other service files)
├── utils/
│   └── session-monitor.ts
├── types/
│   └── index.ts         # TypeScript type definitions
├── data/
│   └── mockData.ts      # Development mock data
├── App.tsx              # Main application component
├── main.tsx             # Application entry point
└── index.css            # Global styles
```

## Component Architecture

### View Components

Main application views (18 components):
- `LoginScreen.tsx` - Authentication
- `DashboardView.tsx` - Overview dashboard
- `KanbanView.tsx` - Kanban board
- `ListView.tsx` - Task list view
- `CalendarView.tsx` - Calendar view
- `GanttView.tsx` - Gantt chart
- `WorkloadView.tsx` - Team workload
- `TeamView.tsx` - Team management
- `ProjectsView.tsx` - Project management
- `ReportsView.tsx` - Reports and analytics
- `ProfileView.tsx` - User profile

### Dialog Components

Modal dialogs for user interactions:
- `TaskDialog.tsx` - Create/edit tasks
- `ProjectDialog.tsx` - Create/edit projects
- `UserProfileDialog.tsx` - Edit user profile
- `ChangePasswordDialog.tsx` - Change password
- `SessionTimeoutDialog.tsx` - Session timeout warning

### Utility Components

Helper components:
- `ProjectSelector.tsx` - Project selection dropdown
- `ViewModeToggle.tsx` - View mode switcher

### UI Components (47 components)

Complete shadcn/ui component library in `components/ui/`:
- accordion, alert, alert-dialog, aspect-ratio
- avatar, badge, breadcrumb, button
- calendar, card, carousel, checkbox
- collapsible, command, context-menu, dialog
- drawer, dropdown-menu, form, hover-card
- input, input-otp, label, menubar
- navigation-menu, pagination, popover, progress
- radio-group, resizable, scroll-area, select
- separator, sheet, skeleton, slider
- sonner, switch, table, tabs
- textarea, toast, toaster, toggle
- toggle-group, tooltip

## State Management

### Current Approach

ProjectGoat currently uses **React state** and **prop drilling** for state management.

**Considerations for scaling:**
- Consider adding Context API for shared state
- Consider Zustand or Redux for complex state
- Current approach works well for current app size

## API Services

### Service Layer Pattern

API calls are organized in service files (`services/` directory):

```typescript
// Example: services/tasks.ts
import api from './api';

export const tasksService = {
  getAll: async () => {
    const response = await api.get('/tasks');
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },

  create: async (task: CreateTaskDTO) => {
    const response = await api.post('/tasks', task);
    return response.data;
  },

  // ... other methods
};
```

### API Client Configuration

Base configuration in `services/api.ts`:
- Base URL from environment
- CSRF token handling
- Session ID management
- Error interceptors

## Authentication Flow

### Session Management

1. User logs in via `LoginScreen.tsx`
2. Backend returns `session_id` and `csrf_token`
3. Tokens stored in state and included in subsequent requests
4. Session monitor tracks activity and timeout
5. User logged out on timeout or manual logout

### Protected Routes

All views except `LoginScreen` require authentication.

## Styling

### TailwindCSS

Utility-first CSS framework:

```tsx
// Example
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <h2 className="text-lg font-semibold">Task Title</h2>
  <Button className="ml-auto">Edit</Button>
</div>
```

### CSS Variables

Theme customization via CSS variables (defined in `index.css`):
- Colors
- Border radius
- Spacing
- Fonts

### Dark Mode

*TODO: Dark mode support using next-themes*

## Forms

### React Hook Form

Form management with validation:

```tsx
import { useForm } from 'react-hook-form';

const { register, handleSubmit, formState: { errors } } = useForm();

<form onSubmit={handleSubmit(onSubmit)}>
  <Input
    {...register('title', { required: 'Title is required' })}
    placeholder="Task title"
  />
  {errors.title && <span>{errors.title.message}</span>}
</form>
```

## Development Workflow

### Running Development Server

```bash
npm run dev
```

Server runs on `http://localhost:3000`

### Building for Production

```bash
npm run build
```

Outputs to `build/` directory

### Type Checking

```bash
npx tsc --noEmit
```

### Linting

```bash
npm run lint  # If configured
```

## Adding a New View

1. **Create view component:**
   ```tsx
   // src/components/NewView.tsx
   export function NewView() {
     return (
       <div>
         <h1>New View</h1>
         {/* Your content */}
       </div>
     );
   }
   ```

2. **Add to main app:**
   Update `App.tsx` to include new view

3. **Add navigation:**
   Update navigation menu to link to new view

4. **Create service (if needed):**
   Add API service in `services/` if new data needed

## Adding a New Component

1. **Create in appropriate directory:**
   - UI components → `components/ui/`
   - Views → `components/`
   - Dialogs → `components/`

2. **Export from component:**
   ```tsx
   export function MyComponent({ prop1, prop2 }: Props) {
     // Component logic
   }
   ```

3. **Import and use:**
   ```tsx
   import { MyComponent } from './components/MyComponent';
   ```

## TypeScript Types

### Defining Types

Types are defined in `types/index.ts`:

```typescript
export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'To Do' | 'In Progress' | 'Done';
  priority: 'low' | 'medium' | 'high';
  assignee_id?: string;
  project_id?: string;
  // ... other fields
}
```

### Using Types

```tsx
import { Task } from '../types';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
}

function TaskCard({ task, onEdit }: TaskCardProps) {
  // Component implementation
}
```

## Best Practices

1. **Component Organization:**
   - One component per file
   - Related components in same directory
   - Clear naming conventions

2. **Props:**
   - Destructure props
   - Use TypeScript interfaces
   - Document complex props

3. **State:**
   - Keep state local when possible
   - Lift state up when needed by multiple components
   - Use appropriate hooks (useState, useEffect, etc.)

4. **Performance:**
   - Use React.memo for expensive components
   - Avoid inline function definitions in props
   - Use useCallback and useMemo appropriately

5. **Accessibility:**
   - Use semantic HTML
   - Include ARIA labels
   - Ensure keyboard navigation works
   - Test with screen readers

6. **Code Style:**
   - Prettier for formatting
   - ESLint for linting (when configured)
   - Consistent naming conventions
   - Clear, self-documenting code

## Icons

### Lucide React

Icon library with 1000+ icons:

```tsx
import { Check, X, Edit, Trash } from 'lucide-react';

<Button>
  <Check className="mr-2 h-4 w-4" />
  Save
</Button>
```

Browse icons: https://lucide.dev/icons/

## Troubleshooting

### Common Issues

**Issue:** Port 3000 already in use
- **Solution:** `netstat -ano | findstr :3000` and kill process

**Issue:** TypeScript errors
- **Solution:** Run `npx tsc --noEmit` to see all errors

**Issue:** Components not updating
- **Solution:** Check React DevTools, verify state changes, ensure keys are unique

**Issue:** API calls failing
- **Solution:** Check Network tab, verify CSRF token, check session validity

## Future Enhancements

- [ ] Add unit tests (React Testing Library)
- [ ] Add Storybook for component documentation
- [ ] Implement dark mode
- [ ] Add internationalization (i18n)
- [ ] Add state management library (if needed)
- [ ] Optimize bundle size
- [ ] Add PWA support

## Resources

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Radix UI Documentation](https://www.radix-ui.com/)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
- [Lucide Icons](https://lucide.dev/)

---

**See Also:**
- [Testing Guide](testing.md)
- [API Reference](../reference/api-endpoints.md)
- [Contributing Guide](../../CONTRIBUTING.md)
