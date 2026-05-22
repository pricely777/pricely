import { createClient } from "@supabase/supabase-js";
type Produto = {
  id: number;
  loja: string;
  produto: string;
  preco: string;
  preco_num: number;
  pesquisa: string;
  data: string;
};
const supabase = createClient(
  "https://umejembwtzlsmedvwcgi.supabase.co",
  "sb_publishable_yA4ZIzW8YeDZ0hTs6Lj0ZA_sYkIEvQe"
);
export default async function DashboardPage() {
  const { data, error } = await supabase
    .from("produtos")
    .select("id, loja, produto, preco, preco_num, pesquisa, data")
    .order("pesquisa", { ascending: true })
    .order("preco_num", { ascending: true });
  const produtos: Produto[] = data ?? [];
  const totalProdutos = produtos.length;
  const lojasUnicas = new Set(produtos.map((p) => p.loja)).size;
  const precosValidos = produtos
    .map((p) => p.preco_num)
    .filter((v): v is number => typeof v === "number" && !Number.isNaN(v));
  const melhorPreco = precosValidos.length ? Math.min(...precosValidos) : 0;
  const piorPreco = precosValidos.length ? Math.max(...precosValidos) : 0;
  const diferencaMaxima = piorPreco - melhorPreco;
  const porPesquisa = produtos.reduce<Record<string, Produto[]>>((acc, item) => {
    const chave = item.pesquisa || "Sem pesquisa";
    if (!acc[chave]) acc[chave] = [];
    acc[chave].push(item);
    return acc;
  }, {});
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#fff", color: "#111" }}>
      <aside
        style={{
          width: 260,
          background: "#0A3D2B",
          color: "#fff",
          padding: 24,
          boxSizing: "border-box",
        }}
      >
        <h2 style={{ marginTop: 0 }}>Pricely</h2>
        <p style={{ opacity: 0.85 }}>Dashboard</p>
      </aside>
      <main style={{ flex: 1, padding: 24, boxSizing: "border-box" }}>
        <h1 style={{ marginTop: 0 }}>Dashboard</h1>
        {error ? (
          <p style={{ color: "crimson" }}>Erro ao carregar dados: {error.message}</p>
        ) : (
          <>
            <section
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                gap: 12,
                marginBottom: 24,
              }}
            >
              <MetricCard label="Total produtos" value={String(totalProdutos)} />
              <MetricCard label="Lojas únicas" value={String(lojasUnicas)} />
              <MetricCard label="Melhor preço" value={formatEuro(melhorPreco)} />
              <MetricCard label="Diferença máxima" value={formatEuro(diferencaMaxima)} />
            </section>
            <section>
              <h2>Produtos por pesquisa</h2>
              {Object.keys(porPesquisa).length === 0 ? (
                <p>Sem dados.</p>
              ) : (
                Object.entries(porPesquisa).map(([pesquisa, itens]) => (
                  <div
                    key={pesquisa}
                    style={{
                      border: "1px solid #e5e7eb",
                      borderRadius: 8,
                      padding: 12,
                      marginBottom: 12,
                    }}
                  >
                    <h3 style={{ marginTop: 0 }}>{pesquisa}</h3>
                    <ul style={{ margin: 0, paddingLeft: 18 }}>
                      {itens.map((p) => (
                        <li key={p.id}>
                          <strong>{p.produto}</strong> — {p.loja} —{" "}
                          {typeof p.preco_num === "number" ? formatEuro(p.preco_num) : p.preco} —{" "}
                          {new Date(p.data).toLocaleString("pt-PT")}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: 10,
        padding: 14,
        background: "#fff",
      }}
    >
      <div style={{ fontSize: 13, color: "#4b5563" }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700 }}>{value}</div>
    </div>
  );
}
function formatEuro(value: number) {
  return new Intl.NumberFormat("pt-PT", {
    style: "currency",
    currency: "EUR",
  }).format(value || 0);
}