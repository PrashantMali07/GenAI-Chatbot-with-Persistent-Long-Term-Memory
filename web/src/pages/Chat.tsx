import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { AlertCircle, RotateCcw } from 'lucide-react';

import { Sidebar } from '../components/Sidebar';
import { ChatInput } from '../components/ChatInput';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Chat() {
  const { threadId } = useParams();
  const navigate = useNavigate();
  const token = useAuthStore((state) => state.token);

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // Guards against a stale history request overwriting newer content:
  // track which thread the last load was for.
  const loadedThreadIdRef = useRef<string | null | undefined>(undefined);

  useEffect(() => {
    if (threadId) {
      // Skip if this thread's content is already loaded/owned locally (e.g.
      // right after creating it and navigating to /c/<id>) — refetching here
      // would wipe the optimistic messages mid-stream.
      if (loadedThreadIdRef.current === threadId) return;
      loadHistory(threadId);
    } else {
      loadedThreadIdRef.current = null;
      setMessages([]);
      setLoadError(null);
    }
  }, [threadId]);

  useEffect(() => {
    // Auto-scroll to bottom
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadHistory = async (id: string) => {
    loadedThreadIdRef.current = id;
    try {
      const res = await api.get(`/api/threads/${id}/history`);
      // Only apply if the user is still viewing this thread — otherwise a
      // slow response for a previous thread would clobber current messages.
      if (loadedThreadIdRef.current !== id) return;
      setMessages(res.data.messages ?? []);
      setLoadError(null);
    } catch (err: any) {
      if (loadedThreadIdRef.current !== id) return;
      console.error('Failed to load history', err);
      setMessages([]);
      setLoadError(err.response?.status
        ? `Couldn't load history (HTTP ${err.response.status}).`
        : "Couldn't load history. Is the backend running at http://localhost:8000?");
    }
  };

  const handleSendMessage = async (text: string) => {
    if (isSending) return; // prevent double-send while a reply is in flight
    let currentThreadId = threadId;

    // If no thread, create one first
    try {
      if (!currentThreadId) {
        const res = await api.post('/api/threads');
        currentThreadId = res.data.thread_id;
        // Mark ownership BEFORE navigating so the threadId effect doesn't
        // clobber local state, then move the URL to /c/<id>.
        loadedThreadIdRef.current = currentThreadId;
        navigate(`/c/${currentThreadId}`, { replace: true });
      }
      setMessages((prev) => [...prev, { role: 'user', content: text }]);
    } catch (err) {
      console.error('Failed to create thread', err);
      return;
    }

    setIsSending(true);
    setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);
    setIsStreaming(true);

    try {
      // SSE Streaming Fetch Call (same-origin — the Vite dev server proxies /api)
      const response = await fetch(`/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          thread_id: currentThreadId,
          message: text,
          stream: true,
        }),
      });

      if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        try {
          const data = await response.json();
          if (data?.detail) detail = typeof data.detail === 'string' ? data.detail : detail;
        } catch { /* not JSON */ }
        throw new Error(`Chat request failed: ${detail}`);
      }
      if (!response.body) throw new Error('No response body');

      // Buffer-accumulator SSE parser: SSE frames can arrive split across
      // TCP chunks, so never parse per-chunk. Frame format: "data: {...}\n\n".
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';
      let streamDone = false;
      let assistantContent = '';

      while (!streamDone) {
        const { value, done: readerDone } = await reader.read();
        if (value) buf += decoder.decode(value, { stream: true });
        if (readerDone) break;

        // Process every complete SSE frame available in the buffer.
        let sep: number;
        while ((sep = buf.indexOf('\n\n')) !== -1 && !streamDone) {
          const frame = buf.slice(0, sep);
          buf = buf.slice(sep + 2);
          const dataStr = frame.startsWith('data: ') ? frame.slice(6).trim() : '';
          if (!dataStr) continue;
          try {
            const data = JSON.parse(dataStr);
            if (data.token) {
              assistantContent += data.token;
              setMessages((prev) => {
                if (prev.length === 0) return prev;
                const newMsgs = [...prev];
                newMsgs[newMsgs.length - 1] = {
                  role: 'assistant',
                  content: assistantContent,
                };
                return newMsgs;
              });
            }
            if (data.done) streamDone = true;
          } catch (e) {
            console.error('SSE parse error', e, dataStr);
          }
        }
      }

      if (!assistantContent) {
        setMessages((prev) => {
          const newMsgs = [...prev];
          if (newMsgs.length && newMsgs[newMsgs.length - 1].role === 'assistant' && !newMsgs[newMsgs.length - 1].content) {
            newMsgs[newMsgs.length - 1] = {
              role: 'assistant',
              content: '*(no reply received)*',
            };
          }
          return newMsgs;
        });
      }
      // After a reply completes, mirror the authoritative server-side state.
      try {
        const res = await api.get(`/api/threads/${currentThreadId}/history`);
        setMessages(res.data.messages);
      } catch (err) {
        console.error('Failed to refresh history after reply', err);
      }
    } catch (err: any) {
      console.error('Streaming failed', err);
      setMessages((prev) => {
        const newMsgs = [...prev];
        const last = newMsgs.length - 1;
        if (last >= 0 && newMsgs[last].role === 'assistant' && !newMsgs[last].content) {
          newMsgs[last] = {
            role: 'assistant',
            content: `⚠️ Failed to get a reply: ${err.message}. Please try again.`,
          };
        }
        return newMsgs;
      });
    } finally {
      setIsStreaming(false);
      setIsSending(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar isOpen={sidebarOpen} toggle={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex-1 flex flex-col min-w-0 relative">
        <div className="border-b p-3 flex justify-end min-h-[56px]">
          {threadId ? (
            <button
              onClick={async () => {
                try {
                  await api.post('/api/memory/summarize', { thread_id: threadId });
                  alert('Successfully summarized to Long-Term Memory!');
                } catch (err) {
                  console.error(err);
                  alert('Failed to summarize.');
                }
              }}
              className="px-3 py-1.5 text-xs font-medium rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors"
            >
              Summarize to Long-Term Memory
            </button>
          ) : (
            <div className="flex items-center text-sm text-muted-foreground px-3">
              New chat — messages are saved once sent
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
          {loadError && (
            <div className="mx-auto max-w-md flex flex-col items-center text-center bg-destructive/10 text-destructive rounded-lg p-4 gap-2">
              <AlertCircle size={24} />
              <p className="text-sm">{loadError}</p>
              <button
                onClick={() => { if (threadId) { setLoadError(null); loadHistory(threadId); } }}
                className="flex items-center gap-1.5 text-xs mt-1 underline hover:no-underline"
              >
                <RotateCcw size={12} /> Retry
              </button>
            </div>
          )}
          {messages.length === 0 && !loadError ? (
            <div className="h-full flex flex-col items-center justify-center text-center opacity-50">
              <h2 className="text-2xl font-bold mb-2">How can I help you today?</h2>
              <p className="max-w-md text-sm">I have long-term memory! Tell me your name or preferences, and I'll remember them across all your chats.</p>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                      m.role === 'user'
                        ? 'bg-primary text-primary-foreground rounded-br-none'
                        : 'bg-muted text-foreground rounded-bl-none'
                    }`}
                  >
                    <div className="text-sm leading-relaxed overflow-hidden">
                      {m.role === 'user' ? (
                        <div className="whitespace-pre-wrap font-medium">{m.content}</div>
                      ) : (
                        <div className="prose prose-sm dark:prose-invert max-w-none break-words">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code({ node, className, children, ...props }: any) {
                              const match = /language-(\w+)/.exec(className || '')
                              const inline = !match && !(String(children).includes('\n'))
                              return !inline && match ? (
                                <SyntaxHighlighter
                                  {...props}
                                  children={String(children).replace(/\n$/, '')}
                                  style={vscDarkPlus as any}
                                  language={match[1]}
                                  PreTag="div"
                                  className="rounded-md my-2"
                                />
                              ) : (
                                <code
                                  {...props}
                                  className="bg-primary/20 px-1 py-0.5 rounded text-primary-foreground font-mono text-xs"
                                >
                                  {children}
                                </code>
                              )
                            },
                          }}
                        >
                          {String(m.content || '') + (isStreaming && i === messages.length - 1 ? ' ▍' : '')}
                        </ReactMarkdown>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <ChatInput onSendMessage={handleSendMessage} disabled={isSending} />
      </div>
    </div>
  );
}
