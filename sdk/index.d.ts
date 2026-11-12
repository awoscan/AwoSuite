export interface AwoToolDescriptor {
  slug: string;
  prefix: string;
  name: string;
  descEn: string;
  descTr: string;
}

export interface AwoMountOptions {
  tool?: string;
  lang?: "tr" | "en";
  width?: string;
  height?: string;
}

export declare const version: string;
export declare const tools: AwoToolDescriptor[];
export declare function getStudioUrl(slug?: string, lang?: "tr" | "en"): string;
export declare function mountWidget(container: string | HTMLElement, options?: AwoMountOptions): HTMLIFrameElement | null;

