import Image from 'next/image';

export default function AssetDisplay() {
  return (
    <div className="hidden bg-gray-100 dark:bg-gray-800 lg:block">
      <Image
        alt="Placeholder"
        className="h-full w-full object-cover"
        height="1080"
        src="/placeholder.png"
        style={{
          aspectRatio: "1920/1080",
          objectFit: "cover",
        }}
        width="1920"
      />
    </div>
  );
}
