# Sistema de Gestão de Comissões - Objetiva Solução

Sistema completo para gestão de comissões de vendas com autenticação de usuários, dashboard profissional e cálculo automático de comissões.

## Funcionalidades

### Autenticação
- **Usuário Master (Thiago)**: Acesso completo ao sistema
  - Email: thiago@objetivasolucao.com.br
  - Senha: vendas123
  
- **Usuário Visualizador (Dalzia)**: Visualização e marcação de pagamentos
  - Email: dalzia.reis@objetivasolucao.com.br
  - Senha: dalzia123
  
- **Vendedores**: Visualização das próprias comissões
  - Email: [email do vendedor cadastrado]
  - Senha: vendas123

### Dashboard Profissional
- Estatísticas em tempo real
- Indicadores visuais de progresso
- Gráficos de status de pagamentos
- Resumo financeiro

### Gestão de Vendedores
- Cadastro completo de vendedores
- Controle de acesso por email
- Histórico de admissão

### Gestão de Oportunidades
- Cadastro de oportunidades de venda
- Cálculo automático de comissões (10% sobre valor líquido)
- Desconto automático de 15% sobre valor bruto
- Vinculação com vendedores

### Gestão de Parcelas
- Controle detalhado de parcelas
- Status visuais para pagamentos
- Indicador especial para primeira mensalidade
- Marcação de recebimento e pagamento de comissão

## Características Técnicas

### Cálculo de Comissões
- **Valor Líquido**: Valor total - 15% (desconto automático)
- **Comissão**: 10% sobre o valor líquido
- **Exemplo**: Venda de R$ 1.000,00
  - Valor líquido: R$ 850,00 (R$ 1.000,00 - 15%)
  - Comissão: R$ 85,00 (10% de R$ 850,00)

### Formato de Datas
- Todas as datas são exibidas no formato brasileiro: DD/MM/AAAA
- Interface intuitiva para entrada de datas

### Indicadores Visuais
- 🟢 Verde: Comissão paga / Parcela recebida
- 🟡 Amarelo: Comissão pendente
- 🔵 Azul pulsante: Primeira mensalidade (destaque especial)

### Banco de Dados
- SQLite para máxima compatibilidade
- Estrutura otimizada para performance
- Backup automático dos dados

## Deployment no Render

### Pré-requisitos
1. Conta no Render (render.com)
2. Repositório Git com o código

### Passos para Deploy
1. Faça upload dos arquivos para um repositório Git
2. Conecte o repositório ao Render
3. O Render detectará automaticamente o arquivo `render.yaml`
4. O deploy será feito automaticamente

### Arquivos Necessários
- `app.py` - Aplicação Flask principal
- `requirements.txt` - Dependências Python
- `render.yaml` - Configuração do Render
- `static/index.html` - Frontend da aplicação
- `database/` - Diretório para banco SQLite (criado automaticamente)

## Estrutura do Projeto

```
sistema-comissoes-final/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências
├── render.yaml           # Configuração Render
├── README.md             # Esta documentação
├── static/
│   └── index.html        # Frontend completo
└── database/
    └── comissoes.db      # Banco SQLite (criado automaticamente)
```

## Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **SQLite**: Banco de dados
- **Flask-CORS**: Suporte a CORS
- **Gunicorn**: Servidor WSGI para produção

### Frontend
- **HTML5/CSS3**: Interface responsiva
- **JavaScript**: Interatividade e comunicação com API
- **Design Responsivo**: Compatível com desktop e mobile

## Segurança

- Autenticação baseada em email/senha
- Controle de acesso por tipo de usuário
- Validação de dados no frontend e backend
- Proteção contra acesso não autorizado

## Suporte

Para suporte técnico ou dúvidas sobre o sistema, entre em contato com a equipe de desenvolvimento.

## Licença

Sistema desenvolvido exclusivamente para Objetiva Solução.

