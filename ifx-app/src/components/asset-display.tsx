import { Card } from "@/components/ui/card";

export default function AssetDisplay({ asset }: { asset: any }) {
  return (
    <div className="relative group">
      <div className="absolute inset-0 bg-gradient-to-br from-accent/20 via-accent/10 to-transparent rounded-2xl blur-xl image-panel-glow"></div>
      <div className="relative w-80 h-96 overflow-hidden rounded-2xl shadow-2xl border-2 border-accent/30 image-panel-float transition-all duration-500 group-hover:scale-105 group-hover:shadow-accent/50 group-hover:border-accent/60">
        <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-accent/20 z-10"></div>
        <img
          src={asset ? asset.url : "/huge_landing.png"}
          alt="AI Assistant"
          className="w-full h-full object-cover transition-all duration-500 group-hover:brightness-110 group-hover:scale-110"
        />
        <div className="absolute inset-0 rounded-2xl border border-accent/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <div className="absolute bottom-0 left-0 right-0 p-6 z-20">
          <div className="text-center">
            <h2 className="text-xl font-bold text-foreground mb-2">AI Assistant</h2>
            <p className="text-sm text-accent font-medium">Powered by Advanced AI</p>
          </div>
        </div>
      </div>
      <div className="absolute -top-2 -right-2 w-4 h-4 bg-accent rounded-full animate-pulse"></div>
      <div className="absolute -bottom-2 -left-2 w-3 h-3 bg-accent/70 rounded-full animate-pulse delay-1000"></div>
    </div>
  );
}