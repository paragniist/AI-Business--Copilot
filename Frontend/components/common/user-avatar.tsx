'use client';

import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';

interface UserAvatarProps {
  name?: string;
  email?: string;
  avatarUrl?: string;
}

export function UserAvatar({ name, email, avatarUrl }: UserAvatarProps) {
  const initials = name
    ? name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
    : (email?.[0] || '?').toUpperCase();

  return (
    <Avatar className="h-8 w-8">
      {avatarUrl && <AvatarImage src={avatarUrl} alt={name || email} />}
      <AvatarFallback>{initials}</AvatarFallback>
    </Avatar>
  );
}
