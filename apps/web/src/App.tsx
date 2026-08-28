import React, { useState } from 'react';
import { Bot, Shield, BookOpen, Layers, Activity } from 'lucide-react';

import { SeatManager } from './components/SeatManager';
import { RhsPanel } from './components/RhsPanel';
import { InteractiveCard } from './components/InteractiveCard';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'seats' | 'rhs' | 'card'>('seats');

  return (
    <div className="container">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ background: 'linear-gradient(135deg, #6366f1, #06b6d4)', padding: '0.6rem', borderRadius: '10px', display: 'flex' }}>
            <Layers size={24} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 700, letterSpacing: '-0.02em' }}>Hikmah（群贤）治理控制台</h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Mattermost × QwenPaw × AgentScope 人机协作薄治理层
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span className="badge badge-active">
            <Activity size={12} /> API 在线
          </span>
          <span className="badge badge-mattermost">Mattermost v11.10+</span>
        </div>
      </header>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '2rem' }}>
        <button
          className={activeTab === 'seats' ? 'btn-primary' : 'glass-panel'}
          style={{ padding: '0.5rem 1.25rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}
          onClick={() => setActiveTab('seats')}
        >
          <Bot size={16} /> 专家席位绑定 (Seats)
        </button>
        <button
          className={activeTab === 'rhs' ? 'btn-primary' : 'glass-panel'}
          style={{ padding: '0.5rem 1.25rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}
          onClick={() => setActiveTab('rhs')}
        >
          <BookOpen size={16} /> 知识人审面板 (Promotion RHS)
        </button>
        <button
          className={activeTab === 'card' ? 'btn-primary' : 'glass-panel'}
          style={{ padding: '0.5rem 1.25rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}
          onClick={() => setActiveTab('card')}
        >
          <Shield size={16} /> 交互卡片预览 (Custom Post)
        </button>
      </div>

      {/* Content */}
      <main>
        {activeTab === 'seats' && <SeatManager />}
        {activeTab === 'rhs' && (
          <div style={{ maxWidth: '480px', margin: '0 auto' }}>
            <RhsPanel />
          </div>
        )}
        {activeTab === 'card' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', alignItems: 'center' }}>
            <InteractiveCard />
          </div>
        )}
      </main>

      <footer style={{ marginTop: '4rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1.5rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Hikmah Control Plane · Python 3.14 + FastAPI + React 19 + Mattermost Web App Plugin
      </footer>
    </div>
  );
};
