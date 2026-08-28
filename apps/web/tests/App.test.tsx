import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { App } from '../src/App';


describe('Hikmah Web Console App', () => {
  it('renders application header and title', () => {
    render(<App />);
    expect(screen.getByText(/Hikmah（群贤）治理控制台/i)).toBeDefined();
    expect(screen.getByText(/专家席位与身份绑定/i)).toBeDefined();
  });
});
