import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Plus, MessageSquare, LogOut, PanelLeftClose, PanelLeft, MoreHorizontal, Trash2 } from 'lucide-react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';

interface Thread {
  thread_id: string;
  label: string;
}

export function Sidebar({ isOpen, toggle }: { isOpen: boolean; toggle: () => void }) {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [menuOpen, setMenuOpen] = useState<string | null>(null);
  const navigate = useNavigate();
  const { threadId } = useParams();
  const { username, logout } = useAuthStore();

  useEffect(() => {
    loadThreads();
  }, [threadId]);

  const loadThreads = async () => {
    try {
      const res = await api.get('/api/threads');
      setThreads(res.data.threads);
    } catch (err) {
      console.error('Failed to load threads', err);
    }
  };

  const createNewChat = async () => {
    try {
      const res = await api.post('/api/threads');
      setThreads([res.data, ...threads]);
      navigate(`/c/${res.data.thread_id}`);
    } catch (err) {
      console.error('Failed to create chat', err);
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await api.delete(`/api/threads/${id}`);
      setThreads(threads.filter(t => t.thread_id !== id));
      if (threadId === id) {
        navigate('/');
      }
    } catch (err) {
      console.error('Failed to delete thread', err);
    }
    setMenuOpen(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isOpen) {
    return (
      <button 
        onClick={toggle} 
        className="absolute top-4 left-4 p-2 bg-background border rounded-md shadow-sm z-10 hover:bg-secondary transition-colors"
      >
        <PanelLeft size={20} />
      </button>
    );
  }

  return (
    <div className="w-64 h-full bg-secondary border-r flex flex-col transition-all relative">
      <div className="p-4 flex items-center justify-between">
        <button
          onClick={createNewChat}
          className="flex-1 flex items-center gap-2 bg-background border rounded-md px-3 py-2 text-sm font-medium hover:bg-muted transition-colors mr-2"
        >
          <Plus size={16} /> New Chat
        </button>
        <button onClick={toggle} className="p-2 text-muted-foreground hover:text-foreground">
          <PanelLeftClose size={20} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {threads.map((t) => (
          <div key={t.thread_id} className="relative group flex items-center">
            <button
              onClick={() => navigate(`/c/${t.thread_id}`)}
              className={`flex-1 flex items-center gap-2 px-3 py-2 text-sm rounded-md truncate transition-colors ${
                threadId === t.thread_id 
                  ? 'bg-primary text-primary-foreground' 
                  : 'text-secondary-foreground hover:bg-background/60'
              }`}
            >
              <MessageSquare size={16} className="shrink-0" />
              <span className="truncate flex-1 text-left">{t.label}</span>
            </button>
            
            <button 
              onClick={(e) => { e.stopPropagation(); setMenuOpen(menuOpen === t.thread_id ? null : t.thread_id); }}
              className={`absolute right-1 p-1 rounded-md opacity-0 group-hover:opacity-100 transition-opacity ${
                threadId === t.thread_id ? 'text-primary-foreground hover:bg-primary-foreground/20' : 'text-muted-foreground hover:bg-muted'
              }`}
            >
              <MoreHorizontal size={16} />
            </button>
            
            {menuOpen === t.thread_id && (
              <div className="absolute right-0 top-8 w-32 bg-popover border border-border rounded-md shadow-md z-50 py-1">
                <button 
                  onClick={(e) => handleDelete(e, t.thread_id)}
                  className="w-full text-left px-4 py-2 text-sm text-destructive hover:bg-muted flex items-center gap-2"
                >
                  <Trash2 size={14} /> Delete
                </button>
              </div>
            )}
          </div>
        ))}
        {threads.length === 0 && (
          <p className="text-xs text-muted-foreground text-center mt-10 px-4">
            No history yet. Send a message to start!
          </p>
        )}
      </div>

      <div className="p-4 border-t border-border flex items-center justify-between">
        <div className="flex items-center gap-2 truncate text-sm font-medium">
          <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold shrink-0">
            {username?.[0]?.toUpperCase() || 'U'}
          </div>
          <span className="truncate">{username}</span>
        </div>
        <button 
          onClick={handleLogout}
          className="p-2 text-muted-foreground hover:text-destructive transition-colors"
          title="Logout"
        >
          <LogOut size={18} />
        </button>
      </div>
    </div>
  );
}
