import { useState } from 'react';
import { Team } from '../types';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { Building2, ChevronDown, Check, Settings } from 'lucide-react';
import * as authService from '../services/auth';
import { toast } from 'sonner';

interface TeamSwitcherProps {
  currentTeam: Team;
  teams: Team[];
  onTeamSwitch: (team: Team) => void;
  onTeamSettingsClick: () => void;
}

export function TeamSwitcher({
  currentTeam,
  teams,
  onTeamSwitch,
  onTeamSettingsClick,
}: TeamSwitcherProps) {
  const [isSwitching, setIsSwitching] = useState(false);

  const handleTeamSwitch = async (teamId: string) => {
    if (teamId === currentTeam.id) return;

    try {
      setIsSwitching(true);
      const response = await authService.switchTeam(teamId);
      onTeamSwitch(response.team);
      toast.success(`Switched to ${response.team.name}`);
    } catch (err: any) {
      console.error('Failed to switch team:', err);
      toast.error(err.message || 'Failed to switch team');
    } finally {
      setIsSwitching(false);
    }
  };

  // If user only has one team, show a simpler display
  if (teams.length <= 1) {
    return (
      <div className="px-4 py-3 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-blue-100 rounded">
              <Building2 className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider">Team</p>
              <p className="text-sm font-medium truncate max-w-[140px]">{currentTeam.name}</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0"
            onClick={onTeamSettingsClick}
            title="Team Settings"
          >
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>
    );
  }

  // Multi-team display with dropdown
  return (
    <div className="px-4 py-3 border-b">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            className="w-full justify-between h-auto py-2 px-2"
            disabled={isSwitching}
          >
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-blue-100 rounded">
                <Building2 className="w-4 h-4 text-blue-600" />
              </div>
              <div className="text-left">
                <p className="text-xs text-gray-500 uppercase tracking-wider">Team</p>
                <p className="text-sm font-medium truncate max-w-[120px]">
                  {isSwitching ? 'Switching...' : currentTeam.name}
                </p>
              </div>
            </div>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-56">
          <DropdownMenuLabel>Switch Team</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {teams.map((team) => (
            <DropdownMenuItem
              key={team.id}
              onClick={() => handleTeamSwitch(team.id)}
              className="cursor-pointer"
            >
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-2">
                  <Building2 className="w-4 h-4" />
                  <span className="truncate max-w-[160px]">{team.name}</span>
                </div>
                {team.id === currentTeam.id && <Check className="w-4 h-4 text-blue-600" />}
              </div>
            </DropdownMenuItem>
          ))}
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={onTeamSettingsClick} className="cursor-pointer">
            <Settings className="w-4 h-4 mr-2" />
            Team Settings
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
