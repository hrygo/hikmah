import React, { useState } from 'react';
import { Bot, ShieldAlert, Check, X } from 'lucide-react';


interface InteractiveCardProps {
  expertName?: string;
  actionTitle?: string;
  actionDetails?: string;
  requiresApproval?: boolean;
}

export const InteractiveCard: React.FC<InteractiveCardProps> = ({
  expertName = 'Code Review Expert (QwenPaw)',
  actionTitle = '请求执行部署脚本：deploy-staging.sh',
  actionDetails = '此操作将影响 staging 测试环境中的 3 个容器服务。',
  requiresApproval = true,
}) => {
  const [approvedState, setApprovedState] = useState<'pending' | 'approved' | 'rejected'>('pending');

  return (
    <div className="glass-panel" style={{ borderLeft: '4px solid var(--accent-primary)', maxWidth: '600px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bot size={18} color="var(--accent-primary)" />
          <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{expertName}</span>
        </div>
        <span className="badge badge-mattermost" style={{ fontSize: '0.7rem' }}>Custom Post</span>
      </div>

      <div style={{ background: 'var(--bg-glass)', borderRadius: '8px', padding: '0.75rem', marginBottom: '1rem', border: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-amber)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.35rem' }}>
          <ShieldAlert size={16} />
          <span>{actionTitle}</span>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{actionDetails}</p>
      </div>

      {requiresApproval && approvedState === 'pending' && (
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            className="btn-primary"
            style={{ fontSize: '0.85rem' }}
            onClick={() => setApprovedState('approved')}
          >
            <Check size={16} /> 批准执行 (HITL)
          </button>
          <button
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
            onClick={() => setApprovedState('rejected')}
          >
            <X size={16} /> 拒绝
          </button>
        </div>
      )}

      {approvedState === 'approved' && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-emerald)', fontSize: '0.85rem' }}>
          <Check size={16} />
          <span>已批准执行 · 已关联写入 Correlation Record Trace</span>
        </div>
      )}

      {approvedState === 'rejected' && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-rose)', fontSize: '0.85rem' }}>
          <X size={16} />
          <span>已人工拦截并终止执行</span>
        </div>
      )}
    </div>
  );
};
