import { render, screen } from '@testing-library/react';
import ChatInput from './chat-input';

describe('ChatInput', () => {
  it('renders the chat input', () => {
    render(<ChatInput sendMessage={() => {}} />);
    const inputElement = screen.getByPlaceholderText('Type your message...');
    expect(inputElement).toBeInTheDocument();
  });
});
