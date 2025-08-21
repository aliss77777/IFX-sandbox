import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Page from './page';
import { act } from 'react';

global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ token: 'test-token' }),
  } as Response)
);

const mockSend = jest.fn();
const mockClose = jest.fn();

global.WebSocket = jest.fn().mockImplementation(() => ({
  send: mockSend,
  close: mockClose,
  onmessage: jest.fn(),
  onclose: jest.fn(),
  onerror: jest.fn(),
})) as any;

describe('Page component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', async () => {
    await act(async () => {
      render(<Page />);
    });
    expect(screen.getByText('Hello! How can I help you today?')).toBeInTheDocument();
  });

  it('sends a message when sendMessage is called', async () => {
    await act(async () => {
      render(<Page />);
    });

    // Wait for the websocket to be connected
    await waitFor(() => expect(global.WebSocket).toHaveBeenCalledTimes(1));

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByRole('button'));

    expect(mockSend).toHaveBeenCalledWith('Test message');
  });
});
