import React from 'react';
import { UserCheck, Lock, Radio } from 'lucide-react';


export interface SeatItem {
  id: string;
  name: string;
  display_name: string;
  mattermost_username: string;
  runtime_type: string;
  is_personal: boolean;
  owner_user_id?: string;
  status: 'active' | 'disabled';
}

const mockSeats: SeatItem[] = [
  {
    id: 'seat_01',
    name: 'architecture_reviewer',
    display_name: '架构评审专家 (QwenPaw)',
    mattermost_username: 'arch-expert',
    runtime_type: 'qwenpaw_shared',
    is_personal: false,
    status: 'active',
  },
  {
    id: 'seat_02',
    name: 'team_coordinator',
    display_name: '频道协作协调员 (AgentScope Sidecar)',
    mattermost_username: 'hikmah-coordinator',
    runtime_type: 'agentscope_sidecar',
    is_personal: false,
    status: 'active',
  },
  {
    id: 'seat_03',
    name: 'alice_personal',
    display_name: 'Alice 本机私有助理 (QwenPaw)',
    mattermost_username: 'alice-agent',
    runtime_type: 'qwenpaw_personal',
    is_personal: true,
    owner_user_id: 'alice',
    status: 'active',
  },
];

export const SeatManager: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>专家席位与身份绑定 (Expert Seats)</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            将 QwenPaw 专家 Agent 与 AgentScope Sidecar 投影为 Mattermost 席位
          </p>
        </div>
        <span className="badge badge-mattermost">Mattermost v11.10+</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
        {mockSeats.map((seat) => (
          <div key={seat.id} className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {seat.is_personal ? <Lock size={18} color="var(--accent-amber)" /> : <UserCheck size={18} color="var(--accent-primary)" />}
                <strong style={{ fontSize: '0.95rem' }}>{seat.display_name}</strong>
              </div>
              <span className={`badge ${seat.is_personal ? 'badge-personal' : 'badge-active'}`}>
                {seat.is_personal ? 'Owner Only' : 'Shared'}
              </span>
            </div>

            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              <div>Mattermost 账号: <code style={{ color: 'var(--accent-cyan)' }}>@{seat.mattermost_username}</code></div>
              <div>运行时提供方: <code>{seat.runtime_type}</code></div>
              {seat.owner_user_id && <div>专属绑定 Owner: <code>@{seat.owner_user_id}</code></div>}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', color: 'var(--accent-emerald)', marginTop: '0.25rem' }}>
              <Radio size={12} />
              <span>席位状态正常 · 契约测试通过</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
