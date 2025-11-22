import { Briefcase, User } from 'lucide-react';

interface ViewModeToggleProps {
  viewMode: 'project' | 'personal';
  onViewModeChange: (mode: 'project' | 'personal') => void;
}

export function ViewModeToggle({ viewMode, onViewModeChange }: ViewModeToggleProps) {
  return (
    <div className="px-4 py-3 border-b">
      <div className="flex rounded-lg border border-gray-200 bg-gray-50 p-1">
        <button
          onClick={() => onViewModeChange('project')}
          className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            viewMode === 'project'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Briefcase className="w-4 h-4" />
          <span>Project</span>
        </button>
        <button
          onClick={() => onViewModeChange('personal')}
          className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            viewMode === 'personal'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <User className="w-4 h-4" />
          <span>Personal</span>
        </button>
      </div>
    </div>
  );
}
