import Link from "next/link";

import { LatestPost } from "~/app/components/post";
import { api, HydrateClient } from "~/trpc/server";

export default async function Home() {
  const hello = await api.post.hello({ text: "from tRPC" });

  void api.post.getLatest.prefetch();

  return (
    <HydrateClient>
      Home Page
    </HydrateClient>
  );
}
