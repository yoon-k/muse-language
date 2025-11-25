import { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Volume2, Lightbulb, BookOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../stores/authStore';
import { useLearningStore } from '../stores/learningStore';
import { cn } from '../lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  corrections?: Array<{
    original: string;
    corrected: string;
    explanation: string;
  }>;
  vocabulary?: Array<{
    word: string;
    definition: string;
    example: string;
  }>;
  grammarTips?: string[];
  timestamp: Date;
}

export function ConversationPage() {
  const { targetLanguage } = useAuthStore();
  const { addXp } = useLearningStore();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [topic, setTopic] = useState('general');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const topics = [
    { id: 'general', label: '일상 대화', icon: '💬' },
    { id: 'travel', label: '여행', icon: '✈️' },
    { id: 'business', label: '비즈니스', icon: '💼' },
    { id: 'food', label: '음식', icon: '🍽️' },
    { id: 'culture', label: '문화', icon: '🎭' },
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 초기 메시지
  useEffect(() => {
    if (messages.length === 0) {
      const greeting: Message = {
        id: 'welcome',
        role: 'assistant',
        content: getWelcomeMessage(targetLanguage),
        timestamp: new Date(),
      };
      setMessages([greeting]);
    }
  }, [targetLanguage]);

  const getWelcomeMessage = (lang: string) => {
    const messages: Record<string, string> = {
      en: "Hello! I'm MUSE, your AI language tutor. Let's practice English together! What would you like to talk about today?",
      ja: "こんにちは！私はMUSEです。一緒に日本語を練習しましょう！今日は何について話しましょうか？",
      zh: "你好！我是MUSE，你的AI语言老师。让我们一起练习中文吧！今天想聊些什么？",
      es: "¡Hola! Soy MUSE, tu tutor de idiomas. ¡Practiquemos español juntos! ¿De qué te gustaría hablar hoy?",
      fr: "Bonjour ! Je suis MUSE, votre tuteur de langues. Pratiquons le français ensemble ! De quoi aimeriez-vous parler aujourd'hui ?",
    };
    return messages[lang] || messages.en;
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // API 호출 (실제 구현에서는 fetch 사용)
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // 샘플 응답
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "That's great! Your sentence structure is good. Let me share some feedback...",
        corrections: input.length > 10 ? [
          {
            original: input.slice(0, 5),
            corrected: input.slice(0, 5).toUpperCase(),
            explanation: "This is a sample correction for demonstration.",
          },
        ] : undefined,
        vocabulary: [
          {
            word: "practice",
            definition: "To do something repeatedly to improve skill",
            example: "I practice speaking every day.",
          },
        ],
        grammarTips: ["Remember to use present tense for habitual actions."],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      addXp(5); // XP 지급

    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // 실제 구현에서는 Web Speech API 사용
  };

  const speakMessage = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = targetLanguage === 'en' ? 'en-US' : targetLanguage;
    speechSynthesis.speak(utterance);
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Topic Selector */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        {topics.map((t) => (
          <button
            key={t.id}
            onClick={() => setTopic(t.id)}
            className={cn(
              "flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all",
              topic === t.id
                ? "bg-blue-100 text-blue-700"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            )}
          >
            <span>{t.icon}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={cn(
                "flex",
                message.role === 'user' ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-3",
                  message.role === 'user'
                    ? "bg-blue-600 text-white"
                    : "bg-white border border-gray-200"
                )}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                {/* Corrections */}
                {message.corrections && message.corrections.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center gap-1.5 text-xs font-medium text-amber-600 mb-2">
                      <Lightbulb className="w-3.5 h-3.5" />
                      교정
                    </div>
                    {message.corrections.map((c, i) => (
                      <div key={i} className="text-xs bg-amber-50 rounded-lg p-2 mb-1">
                        <div className="line-through text-gray-500">{c.original}</div>
                        <div className="text-green-600 font-medium">{c.corrected}</div>
                        <div className="text-gray-600 mt-1">{c.explanation}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Vocabulary */}
                {message.vocabulary && message.vocabulary.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center gap-1.5 text-xs font-medium text-blue-600 mb-2">
                      <BookOpen className="w-3.5 h-3.5" />
                      새 단어
                    </div>
                    {message.vocabulary.map((v, i) => (
                      <div key={i} className="text-xs bg-blue-50 rounded-lg p-2 mb-1">
                        <div className="font-medium text-blue-700">{v.word}</div>
                        <div className="text-gray-600">{v.definition}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Actions */}
                {message.role === 'assistant' && (
                  <div className="flex gap-2 mt-2">
                    <button
                      onClick={() => speakMessage(message.content)}
                      className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors"
                      title="듣기"
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            placeholder="메시지를 입력하세요..."
            className="w-full px-4 py-3 pr-12 bg-white border border-gray-200 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={1}
          />
          <button
            type="button"
            onClick={toggleRecording}
            className={cn(
              "absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-full transition-colors",
              isRecording
                ? "bg-red-500 text-white"
                : "text-gray-400 hover:text-gray-600"
            )}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>
        </div>

        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className={cn(
            "px-4 py-3 rounded-2xl transition-all",
            input.trim() && !isLoading
              ? "bg-blue-600 text-white hover:bg-blue-700"
              : "bg-gray-200 text-gray-400 cursor-not-allowed"
          )}
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
}
