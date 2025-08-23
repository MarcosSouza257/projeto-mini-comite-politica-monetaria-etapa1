## Etapa 1 — Montando os Cenários 
## PUC-Minas — Ciências Econômicas, 3º período

### Objetivo
Este projeto visa demonstrar a relação entre a Taxa Selic, matemática financeira, decisões de investimento e os canais de transmissão da política monetária, utilizando títulos do Tesouro Direto e simulações em Python. O objetivo é entender como diferentes cenários econômicos afetam o retorno de diversos produtos financeiros.

### Escopo
- **Investimento inicial:** `R$ 100.000,00`
- **Prazo de simulação:** 3 anos (36 meses; 756 dias corridos ≈ 252 dias úteis/ano)
- **Produtos simulados:**
  - **Tesouro Selic 2028:** Capitalização diária com base na Selic.
  - **Tesouro Prefixado 2028:** Taxa fixa de 14% a.a.
  - **Tesouro IPCA+ 2028:** IPCA + juro real de 7% a.a.
  - **CDB 100% do CDI:** Assume CDI ≈ Selic Meta.
  - **LCI 90% da Selic Meta:** Isenta de IR, mas com custódia.
  - **Poupança:** Regras vigentes com TR fixa de 0,17% a.m.
- **Custos e impostos:**
  - **Taxa de custódia:** 0,2% a.a. para Tesouro, CDB e LCI.
  - **Imposto de Renda:** Tabela regressiva (15% para prazo de 3 anos).
  - **IOF:** Desconsiderado (prazos > 30 dias).

---

## Parte 1 — Cenários e parâmetros

### Cenários da Selic e IPCA
- **Cenário 1 (Manutenção):**
  - Selic: 15% a.a. em 2025, 2026 e 2027
  - IPCA: 4,5% a.a. nos 3 anos

- **Cenário 2 (Aperto Monetário):**
  - Selic: 15% (2025), 16,5% (2026), 17% (2027)
  - IPCA: 4,5% (2025), 5,0% (2026), 5,5% (2027)

- **Cenário 3 (Afrouxamento Monetário):**
  - Selic: 15% (2025), 13% (2026), 11% (2027)
  - IPCA: 4% a.a. nos 3 anos

### Regras de rendimento por produto
- **Tesouro Selic 2028:** Rende a Selic efetiva diária.
- **Tesouro Prefixado 2028:** Rende 14% a.a. (taxa fixa), independente de cenário.
- **Tesouro IPCA+ 2028:** Rende IPCA + 7% a.a. (juros reais fixos de 7% a.a.).
- **CDB 100% do CDI:** Rende 100% da taxa DI; CDI fica ~0,1 p.p. abaixo da Selic (conforme B3).
- **LCI:** Rende 90% da Selic Meta (isenta de IR, porém aplica custódia 0,2% a.a. conforme escopo).
- **Poupança:**
  - Se Selic Meta > 8,5% a.a.: 0,5% a.m.
  - Se Selic Meta ≤ 8,5% a.a.: 70% da Selic a.a. (converter para mensal)
  - Em ambos os casos, somamos TR fixa de 0,17% a.m. para todos os cenários

### Custos e impostos
- **Taxa de custódia (Tesouro/CDB/LCI):** 0,2% a.a. — aplicamos de forma proporcional ao período (mensal/diária).
- **IR (alíquota efetiva para 3 anos):** 15% sobre os rendimentos (exceto LCI e Poupança, que são isentas de IR).

---

## Parte 1 — Fórmulas

Use capitalização composta e equivalência de taxas.

### Equivalência de taxas
- De taxa anual para mensal: `i_m = (1 + i_a)^(1/12) - 1`
- De taxa anual para diária útil (252): `i_d = (1 + i_a)^(1/252) - 1`
- Composição inflação + juro real (IPCA+): `i_nominal = (1 + i_ipca) * (1 + i_real) - 1`

### Valor futuro e valor líquido
- **Valor futuro bruto (capitalização composta):** `VF_bruto = VP * (1 + i)^n`
- **Custódia (aprox. por período):**
  - Mensal: `c_m = (1 + 0,002)^(1/12) - 1`
  - Diária útil: `c_d = (1 + 0,002)^(1/252) - 1`
  - Aplicar como encargo recorrente sobre o saldo.
- **Imposto de Renda (quando aplicável):** `IR = 0,15 * (VF_bruto - VP)`
- **Valor futuro líquido:** `VF_liq = VF_bruto - IR - Custódia_acumulada`

### Especificidades por produto
- **Tesouro Selic:** Capitalização diária útil. Use `i_d_selic` a cada dia útil do período.
- **Prefixado 14% a.a.:** Use taxa mensal equivalente `i_m_fix` para 36 períodos mensais.
- **IPCA+ 7% a.a.:** Para cada mês, converta IPCA anual do cenário em taxa mensal `ipca_m`, converta 7% a.a. em `i_m_real`, componha `i_m_nominal = (1+ipca_m)*(1+i_m_real)-1`.
- **CDB 100% CDI:** CDI fica 0,1 p.p. abaixo da Selic (conforme B3), com IR e custódia.
- **LCI 90% Selic:** 90% da Selic Meta (isenta de IR, com custódia).
- **Poupança:** Aplicar regra conforme nível da Selic e capitalizar mensalmente.

---

## Parte 2 — Implementação em Python

### Estrutura do projeto
```
data/                 # saídas Excel (geradas opcionalmente)
figures/              # gráficos PNG (gerados opcionalmente)
src/
  ├── config.py       # configurações centralizadas (capital inicial, taxas, etc.)
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

### Configurações centralizadas (`src/config.py`)
Para alterar facilmente os parâmetros do projeto, edite o arquivo `src/config.py`:

#### Parâmetros da Simulação:
- **CAPITAL_INICIAL:** `100000.0` (R$ 100.000,00) ← **Altere aqui para mudar o valor**
- **ANOS_SIMULACAO:** `3` ← **Altere aqui para mudar o período (1, 2, 3, 5 anos, etc.)**
- **DIAS_UTEIS_POR_ANO:** `252` (padrão do mercado brasileiro)
- **TAXA_CUSTODIA_ANUAL:** `0.002` (0,2% a.a.)
- **ALIQUOTA_IR:** `0.15` (15% - ajustada automaticamente por prazo)
- **TR_MENSAL_FIXA:** `0.0017` (0,17% a.m. para poupança)

**Parâmetros calculados automaticamente:**
- **MESES_SIMULACAO:** `ANOS_SIMULACAO * 12` (36 meses para 3 anos)
- **DIAS_UTEIS_SIMULACAO:** `ANOS_SIMULACAO * 252` (756 dias úteis para 3 anos)

#### Cenários Econômicos:
Os cenários estão definidos no dicionário `CENARIOS` e são **automaticamente incluídos** nas simulações:

```python
CENARIOS = {
    "manutencao": CenarioEconomico(...),    # Cenário 1 - Manutenção
    "aperto": CenarioEconomico(...),        # Cenário 2 - Aperto Monetário  
    "afrouxamento": CenarioEconomico(...),  # Cenário 3 - Afrouxamento
    "recessao": CenarioEconomico(...),      # Cenário 4 - Recessão (exemplo)
}
```

**Para criar um novo cenário:**
1. Adicione uma nova entrada ao dicionário `CENARIOS`
2. Execute `python main.py` - o novo cenário será incluído automaticamente!

**Exemplo - Cenário de Crise (flexível para qualquer número de anos):**
```python
CENARIOS["crise"] = CenarioEconomico(
    nome="Cenario 5 - Crise",
    descricao="Cenário de crise: Selic alta, IPCA descontrolado",
    selic_por_ano=[0.15, 0.25, 0.30, 0.35, 0.40][:ANOS_SIMULACAO],  # Ajusta automaticamente
    ipca_por_ano=[0.045, 0.12, 0.18, 0.25, 0.30][:ANOS_SIMULACAO],  # Ajusta automaticamente
)
```

**Para simular períodos diferentes:**
1. Edite `src/config.py` e altere `ANOS_SIMULACAO = 3` para o valor desejado
2. Execute `python main.py` normalmente

**Exemplos:**
- **1 ano:** `ANOS_SIMULACAO = 1` → 252 dias úteis
- **2 anos:** `ANOS_SIMULACAO = 2` → 504 dias úteis  
- **5 anos:** `ANOS_SIMULACAO = 5` → 1.260 dias úteis
- **10 anos:** `ANOS_SIMULACAO = 10` → 2.520 dias úteis

**⚠️ Importante:** Os cenários devem ter taxas suficientes para o número de anos escolhido. Use listas com `[:ANOS_SIMULACAO]` para ajuste automático.

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
- **Custódia por período:**
  - `c_m = (1+0.002)**(1/12)-1` (mensal)
  - `c_d = (1+0.002)**(1/252)-1` (diária)
- **IR final (quando aplicável):** `ir = 0.15 * max(0, vf_bruto - valor_inicial)`

### Loop de simulação em `simulate.py`
- Recebe: série de taxas por período (por cenário e produto), valor inicial, parâmetros de custos/IR.
- Retorna: série temporal com `saldo_bruto`, `custodia`, `saldo_pos_custodia`, e no fim `vf_bruto`, `ir_final`, `vf_liquido`.
- Pode salvar .xlsx em `data/` e gráficos em `figures/`.

### Como executar
- **Instale as dependências:**
```
pip install -r requirements.txt
```

- **Execute as simulações (valor inicial padrão R$ 100.000,00):**
```
python main.py
```
- **Para salvar resultados (xlsx) e gráficos (PNGs):**
```
python main.py --initial 100000 \
               --save-results --out-dir data \
               --save-figures --fig-dir figures
```
**Saídas:**
- `data/simulacao_por_titulo.xlsx` com aba por produto + aba resumo
- `figures/*_summary.png` com VF líquido por produto