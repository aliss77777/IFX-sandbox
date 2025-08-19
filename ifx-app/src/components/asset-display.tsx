import { Card } from "@/components/ui/card";

export default function AssetDisplay() {
  return (
    <div className="relative group">
      <div className="absolute inset-0 bg-gradient-to-br from-accent/20 via-accent/10 to-transparent rounded-2xl blur-xl image-panel-glow"></div>
      <div className="relative w-80 h-96 overflow-hidden rounded-2xl shadow-2xl border-2 border-accent/30 image-panel-float transition-all duration-500 group-hover:scale-105 group-hover:shadow-accent/50 group-hover:border-accent/60">
        <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-accent/20 z-10"></div>
        <img
          src="https://cdn-lfs-us-1.hf.co/repos/6d/cf/6dcfd431249cc8dbab4c075c36e2d89df484c0a4c5d4177f3c8018678236f2c2/419c79532051653a93698a387b211aa387ad7216a4615d6c62e52c4fcf3ae518?response-content-disposition=inline%3B+filename*%3DUTF-8%27%27huge_landing.png%3B+filename%3D%22huge_landing.png%22%3B&response-content-type=image%2Fpng&Expires=1755635269&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc1NTYzNTI2OX19LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2RuLWxmcy11cy0xLmhmLmNvL3JlcG9zLzZkL2NmLzZkY2ZkNDMxMjQ5Y2M4ZGJhYjRjMDc1YzM2ZTJkODlkZjQ4NGMwYTRjNWQ0MTc3ZjNjODAxODY3ODIzNmYyYzIvNDE5Yzc5NTMyMDUxNjUzYTkzNjk4YTM4N2IyMTFhYTM4N2FkNzIxNmE0NjE1ZDZjNjJlNTJjNGZjZjNhZTUxOD9yZXNwb25zZS1jb250ZW50LWRpc3Bvc2l0aW9uPSomcmVzcG9uc2UtY29udGVudC10eXBlPSoifV19&Signature=rrROFLL-P5iAjXDvnibgcxxrfvloYE64kzpumkUotPzOIRoJg9mZTUOXujYSfy1iOu5jzA-zLyPmHI2ykRr7iYCQRbUykh9WP34B9TfaGjd7fqSGwmP54L70uugQbtyZXZNh5FSCCPmJqgSb79TU3TmtS9qsVZ3Fbs4p9hKzshYrjfm8hUiT6V3oOarb8VcBRhLOPFnPVtgr0EaCXEjy58JlNbRWLZeggInl7e9M%7EHQ1PbNomwU3EiJa184Pw0-oJ9VDHsJsuZ3csSCQRRMXoEN64hHCAxZhw-ETXLKqaI-kQ3notmzBdm6%7EMapSuf0MKySRIzYvWxYy%7ET%7Ezdsuwig__&Key-Pair-Id=K24J24Z295AEI9"
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