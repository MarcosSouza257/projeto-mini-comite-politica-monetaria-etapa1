## Etapa 1 — Montando os Cenários (PUC-Minas — Ciências Econômicas, 3º período)

### Objetivo
demonstrar a relação entre a Taxa Selic, matemática financeira, decisões de investimento e os canais de transmissão da política monetária, utilizando títulos do Tesouro Direto e com simulações em Python.

### Escopo
- Meu investimento inicial: `R$ 100.000,00`
- Prazo de simulação: 3 anos (36 meses; 756 dias corridos ≈ 252 dias úteis/ano)
- Produtos simulados:
  - Tesouro Selic 2028 (capitalização diária)
  - Tesouro Prefixado 2028 (taxa fixa)
  - Tesouro IPCA+ 2028 (IPCA + juro real)
  - CDB 100% do CDI (assumir CDI ≈ Selic Meta)
  - LCI 90% da Selic Meta
  - Poupança (regras vigentes)
- Custos e impostos:
  - Taxa de custódia (aprox.): 0,2% a.a. para Tesouro, CDB e LCI
  - Imposto de Renda: tabela regressiva (15% para prazo de 3 anos)
  - IOF: desconsiderado (prazos > 30 dias)


---

## Parte 1 — Cenários e parâmetros

### Cenários da Selic e IPCA
- Cenário 1 (Manutenção):
  - Selic: 15% a.a. em 2025, 2026 e 2027
  - IPCA: 4,5% a.a. nos 3 anos

- Cenário 2 (Aperto Monetário):
  - Selic: 15% (2025), 16,5% (2026), 17% (2027)
  - IPCA: 4,5% (2025), 5,0% (2026), 5,5% (2027)

- Cenário 3 (Afrouxamento Monetário):
  - Selic: 15% (2025), 13% (2026), 11% (2027)
  - IPCA: 4% a.a. nos 3 anos

### Regras de rendimento por produto
- Tesouro Selic 2028: rende a Selic efetiva diária.
- Tesouro Prefixado 2028: rende 14% a.a. (taxa fixa), independente de cenário.
- Tesouro IPCA+ 2028: rende IPCA + 7% a.a. (juros reais fixos de 7% a.a.).
- CDB 100% do CDI: rende 100% da taxa DI;  DI ≈ Selic Meta.
- LCI: rende 90% da Selic Meta (isenta de IR, porém aplica custódia 0,2% a.a. conforme escopo).
- Poupança:
  - Se Selic Meta > 8,5% a.a.: 0,5% a.m.
  - Se Selic Meta ≤ 8,5% a.a.: 70% da Selic a.a. (converter para mensal)
  - Em ambos os casos, somamos TR fixa de 0,17% a.m. para todos os cenários

### Custos e impostos
- Taxa de custódia (Tesouro/CDB/LCI): 0,2% a.a. — aplicamos de forma proporcional ao período (mensal/diária).
- IR (alíquota efetiva para 3 anos): 15% sobre os rendimentos (exceto LCI e Poupança, que são isentas de IR).

---

## Parte 1 — Fórmulas

Use capitalização composta e equivalência de taxas.

### Equivalência de taxas
- De taxa anual para mensal: `i_m = (1 + i_a)^(1/12) - 1`
- De taxa anual para diária útil (252): `i_d = (1 + i_a)^(1/252) - 1`
- Composição inflação + juro real (IPCA+): `i_nominal = (1 + i_ipca) * (1 + i_real) - 1`

### Valor futuro e valor líquido
- Valor futuro bruto (capitalização composta): `VF_bruto = VP * (1 + i)^n`
- Custódia (aprox. por período):
  - Mensal: `c_m = (1 + 0,002)^(1/12) - 1`
  - Diária útil: `c_d = (1 + 0,002)^(1/252) - 1`
  - Aplicar como encargo recorrente sobre o saldo.
- Imposto de Renda (quando aplicável): `IR = 0,15 * (VF_bruto - VP)`
- Valor futuro líquido: `VF_liq = VF_bruto - IR - Custódia_acumulada`


### Especificidades por produto
- Tesouro Selic: capitalização diária útil. Use `i_d_selic` a cada dia útil do período.
- Prefixado 14% a.a.: use taxa mensal equivalente `i_m_fix` para 36 períodos mensais.
- IPCA+ 7% a.a.: para cada mês, converta IPCA anual do cenário em taxa mensal `ipca_m`, converta 7% a.a. em `i_m_real`, componha `i_m_nominal = (1+ipca_m)*(1+i_m_real)-1`.
- CDB 100% CDI: igual à Selic Meta do cenário (mensal ou diária, conforme granularidade usada), com IR e custódia.
- LCI 90% Selic: 90% da Selic Meta (isenta de IR, com custódia).
- Poupança: aplicar regra conforme nível da Selic e capitalizar mensalmente.

---

## Parte 2 — Implementação em Python

### Estrutura do projeto
```
data/                 # saídas CSV (geradas opcionalmente)
figures/              # gráficos PNG (gerados opcionalmente)
src/
  ├── scenarios.py    # trajetórias de Selic e IPCA por cenário (36 meses)
  ├── rates.py        # conversões de taxas (anual↔mensal↔diária), IPCA+ composição
  ├── products.py     # simuladores: Tesouro, CDB, LCI, Poupança (com TR=0,17% a.m.)
  ├── taxes.py        # utilitários de IR e custódia
  ├── simulate.py     # orquestra simulações por cenário e produz resumos
  └── plots.py        # gráficos comparativos (matplotlib)
main.py               # ponto de entrada (CLI)
requirements.txt      # dependências
README.md
```

### Parâmetros globais no código
- Valor inicial: `100000.00`
- Prazo: `36` meses
- Dias úteis/ano: `252` 
- Custódia a.a.: `0.002` (0,2%)
- IR: `0.15` (para 3 anos, quando aplicável)

### Definição dos cenários em `scenarios.py`
- Função que retorna um DataFrame por cenário com colunas: `ano`, `selic_aa`, `ipca_aa`.
- A partir disso, derive colunas mensais/diárias conforme a granularidade escolhida.

### Conversões de taxa em `rates.py`
- `annual_to_monthly(i_a) = (1+i_a)**(1/12)-1`
- `annual_to_daily(i_a, dias=252) = (1+i_a)**(1/dias)-1`
- `compose_ipca_plus(ipca_m, real_m) = (1+ipca_m)*(1+real_m)-1`

### Produtos em `products.py`
- Implementar funções ou classes com interface comum, por exemplo:
  - `simulate_tesouro_selic(...)`
  - `simulate_tesouro_prefixado(...)` (14% a.a.)
  - `simulate_tesouro_ipca_plus(...)` (IPCA + 7% a.a.)
  - `simulate_cdb_cdi(...)` (100% CDI≈Selic)
  - `simulate_lci(...)` (90% Selic; isenta de IR)
  - `simulate_poupanca(...)` (regras conforme Selic; sem IR e sem custódia)


### Custos e impostos em `taxes.py`
- Custódia por período:
  - `c_m = (1+0.002)**(1/12)-1` (mensal)
  - `c_d = (1+0.002)**(1/252)-1` (diária)
- IR final (quando aplicável): `ir = 0.15 * max(0, vf_bruto - valor_inicial)`

### Loop de simulação em `simulate.py`
- Recebe: série de taxas por período (por cenário e produto), valor inicial, parâmetros de custos/IR.
- Retorna: série temporal com `saldo_bruto`, `custodia`, `saldo_pos_custodia`, e no fim `vf_bruto`, `ir_final`, `vf_liquido`.
- Pode salvar .xlsx em `data/` e gráficos em `figures/`.

### Como executar
- instale as dependências:
```
pip install -r requirements.txt
```
- execute as simulações (valor inicial padrão R$ 100.000,00):
```
python main.py
```
- Para salvar resultados (xlsx) e gráficos (PNGs):
```
python main.py --initial 100000 \
               --save-results --out-dir data \
               --save-figures --fig-dir figures
```
Saídas:
- `data/*_summary.csv` por cenário e `data/resumo_todos_os_cenarios.csv` combinado
- `figures/*_summary.png` com VF líquido por produto

---

## O que o código faz
- Construe as curvas mensais de Selic e IPCA por cenário (36 meses)
- Simula os produtos aplicando capitalização composta, custódia (0,2% a.a. equivalente mensal) e IR (15% no final quando aplicável)
- Na poupança, consideramos TR fixa de 0,17% a.m. somada ao rendimento base
- Eu gero resumos por cenário com VF bruto, IR e VF líquido; e gráficos opcionais

---

## O que analisar no relatório (texto)
- Como as mudanças na Selic impactam cada produto (canais de transmissão).
- Diferença entre retornos nominais e reais (ajustar por IPCA quando pertinente).
- Efeito das taxas (custódia e IR) sobre o ranking dos investimentos.
- Sensibilidade do Tesouro IPCA+ à inflação e do Prefixado à trajetória de juros.
- Decisões de portfólio: qual produto domina em cada cenário e por quê.

---

## Notas finais
- Se desejar maior precisão, utilize granularidade diária para Tesouro Selic e custódia diária para todos os produtos com custódia.
- Documente quaisquer simplificações (ex.: TR≈0, CDI≈Selic) no relatório.
- Valide fórmulas com casos de teste simples (ex.: taxa zero, 1 mês) antes da simulação completa.

