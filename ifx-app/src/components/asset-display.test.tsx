import { render, screen } from '@testing-library/react';
import AssetDisplay from './asset-display';

describe('AssetDisplay component', () => {
  it('renders the default image when no asset is provided', () => {
    render(<AssetDisplay asset={null} />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', '/huge_landing.png');
  });

  it('renders the asset image when an asset is provided', () => {
    const asset = { url: 'https://example.com/image.png' };
    render(<AssetDisplay asset={asset} />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', asset.url);
  });
});
