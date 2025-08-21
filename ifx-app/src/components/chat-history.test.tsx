import { render, screen } from '@testing-library/react';
import ChatHistory, { Message } from './chat-history';

describe('ChatHistory component', () => {
  const history: Message[] = [
    { text: 'Hello', sender: 'user', timestamp: new Date() },
    { text: 'Hi there', sender: 'assistant', timestamp: new Date() },
  ];

  it('renders a list of messages', () => {
    render(<ChatHistory history={history} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there')).toBeInTheDocument();
  });

  it('displays the correct sender for each message', () => {
    render(<ChatHistory history={history} />);
    expect(screen.getByText('U')).toBeInTheDocument();
    expect(screen.getByText('AI')).toBeInTheDocument();
  });
});
