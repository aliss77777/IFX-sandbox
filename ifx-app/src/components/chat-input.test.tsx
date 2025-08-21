import { render, screen, fireEvent } from '@testing-library/react';
import ChatInput from './chat-input';

describe('ChatInput', () => {
  it('renders the chat input', () => {
    render(<ChatInput sendMessage={() => {}} />);
    const inputElement = screen.getByPlaceholderText('Type your message...');
    expect(inputElement).toBeInTheDocument();
  });

  it('calls sendMessage when the send button is clicked', () => {
    const sendMessage = jest.fn();
    render(<ChatInput sendMessage={sendMessage} />);
    const inputElement = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button');

    fireEvent.change(inputElement, { target: { value: 'Hello' } });
    fireEvent.click(sendButton);

    expect(sendMessage).toHaveBeenCalledWith('Hello');
  });

  it('calls sendMessage when the Enter key is pressed', () => {
    const sendMessage = jest.fn();
    render(<ChatInput sendMessage={sendMessage} />);
    const inputElement = screen.getByPlaceholderText('Type your message...');

    fireEvent.change(inputElement, { target: { value: 'Hello' } });
    fireEvent.keyDown(inputElement, { key: 'Enter', code: 'Enter' });

    expect(sendMessage).toHaveBeenCalledWith('Hello');
  });

  it('does not call sendMessage when the message is empty', () => {
    const sendMessage = jest.fn();
    render(<ChatInput sendMessage={sendMessage} />);
    const sendButton = screen.getByRole('button');

    fireEvent.click(sendButton);

    expect(sendMessage).not.toHaveBeenCalled();
  });
});
