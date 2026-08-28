import React from 'react';
import { RhsPanel } from './components/RhsPanel';
import { InteractiveCard } from './components/InteractiveCard';

/**
 * Mattermost Web App Plugin Registry interface.
 * Implements standard extension points:
 * 1. registerRightHandSidebarComponent (Knowledge Promotion / Trace)
 * 2. registerPostTypeComponent (Interactive HITL approval / streaming agent cards)
 * 3. registerChannelHeaderButtonAction
 */
export interface MattermostPluginRegistry {
  registerRightHandSidebarComponent: (component: React.ComponentType, title: string) => { id: string };
  registerPostTypeComponent: (type: string, component: React.ComponentType<{ post: any }>) => void;
  registerChannelHeaderButtonAction: (icon: React.ReactNode, action: () => void, tooltip: string) => void;
}

export class HikmahMattermostPlugin {
  initialize(registry: MattermostPluginRegistry, _store?: unknown) {

    // 1. Register RHS for Knowledge Promotion & Trace Audit
    registry.registerRightHandSidebarComponent(
      () => <RhsPanel />,
      'Hikmah 治理与知识面板'
    );

    // 2. Register Custom Post Type for interactive approval cards
    registry.registerPostTypeComponent('custom_hikmah_action', ({ post }) => (
      <InteractiveCard
        expertName={post?.props?.expert_name}
        actionTitle={post?.props?.action_title}
        actionDetails={post?.props?.action_details}
      />
    ));
  }

  uninitialize() {
    // Cleanup plugin subscriptions
  }
}

// Global window attachment for Mattermost Plugin loader
declare global {
  interface Window {
    registerPlugin: (id: string, plugin: HikmahMattermostPlugin) => void;
  }
}

if (typeof window !== 'undefined' && window.registerPlugin) {
  window.registerPlugin('com.hrygo.hikmah', new HikmahMattermostPlugin());
}
