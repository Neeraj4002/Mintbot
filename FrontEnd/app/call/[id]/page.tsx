import CallPage from "@/app/call/[id]/CallPage";

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
    const resolvedParams = await params;
    return <CallPage id={resolvedParams.id} />;
}