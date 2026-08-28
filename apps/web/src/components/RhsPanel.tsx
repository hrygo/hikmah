import React, { useState } from 'react';
import { BookOpen, CheckCircle, XCircle, ShieldCheck } from 'lucide-react';


export interface KnowledgeCandidateItem {
  id: string;
  title: string;
  summary: string;
  source_channel_id: string;
  proposer_user_id: string;
  status: 'proposed' | 'approved' | 'rejected';
  scope: 'channel' | 'team';
}

interface RhsPanelProps {
  candidates?: KnowledgeCandidateItem[];
  onReview?: (id: string, approved: boolean) => void;
}

export const RhsPanel: React.FC<RhsPanelProps> = ({
  candidates = [
    {
      id: 'know_01',
      title: 'Mattermost Bot Token 配置最佳实践',
      summary: '从生产事故中提炼：Bot Token 需绑定只读权限，严禁赋予 System Admin 权限。',
      source_channel_id: 'town-square',
      proposer_user_id: 'alice',
      status: 'proposed',
      scope: 'team',
    },
  ],
  onReview,
}) => {
  const [items, setItems] = useState<KnowledgeCandidateItem[]>(candidates);

  const handleAction = (id: string, approved: boolean) => {
    setItems((prev) =>
      prev.map((it) => (it.id === id ? { ...it, status: approved ? 'approved' : 'rejected' } : it))
    );
    if (onReview) onReview(id, approved);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BookOpen size={18} color="var(--accent-primary)" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>知识晋升审核 (Promotion RHS)</h3>
        </div>
        <span className="badge badge-active" style={{ fontSize: '0.7rem' }}>人审关卡</span>
      </div>

      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
        群聊中产生的高价值共识需经人工审阅后，方可晋升为团队长期资产。
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {items.map((item) => (
          <div key={item.id} className="glass-panel" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>{item.title}</h4>
              <span className={`badge ${item.status === 'approved' ? 'badge-active' : item.status === 'rejected' ? 'badge-personal' : 'badge-mattermost'}`}>
                {item.status}
              </span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>{item.summary}</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span>提议人: @{item.proposer_user_id}</span>
              <span>范围: {item.scope.toUpperCase()}</span>
            </div>

            {item.status === 'proposed' && (
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button
                  className="btn-primary"
                  style={{ flex: 1, padding: '0.35rem 0.5rem', fontSize: '0.8rem', justifyContent: 'center' }}
                  onClick={() => handleAction(item.id, true)}
                >
                  <CheckCircle size={14} /> 批准晋升
                </button>
                <button
                  style={{
                    flex: 1,
                    background: 'rgba(244, 63, 94, 0.15)',
                    color: '#fb7185',
                    border: '1px solid rgba(244, 63, 94, 0.3)',
                    borderRadius: '8px',
                    fontSize: '0.8rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.35rem',
                  }}
                  onClick={() => handleAction(item.id, false)}
                >
                  <XCircle size={14} /> 驳回
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      <div style={{ marginTop: '1rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-cyan)', fontSize: '0.85rem' }}>
          <ShieldCheck size={16} />
          <span>全链路 Correlation Trace 处于活跃状态</span>
        </div>
      </div>
    </div>
  );
};
