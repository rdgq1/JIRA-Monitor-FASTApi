<!DOCTYPE html>
<html lang="pt-br">

<head>
    <meta charset="UTF-8">
    <title>Monitor de HelpDesk</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            font-family: 'Roboto', Arial, sans-serif;
            background-color: #1a237e;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background-color: white;
            color: #1a237e;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .header img {
            height: 200px;
            margin-right: 15px;
            position: absolute;
            left: 20px;
        }

        .header h1 {
            margin: 0;
            font-size: 2em;
        }

        .header p {
            margin-top: 5px;
            font-size: 0.9em;
            opacity: 0.8;
        }

        .columns {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .col {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            padding: 15px;
            position: relative; /* Adicionado para posicionar o totalizador */
        }

        .col h2 {
            text-align: center;
            margin-bottom: 15px;
            color: #3f51b5;
            border-bottom: 2px solid #3f51b5;
            padding-bottom: 5px;
        }

        .hora {
            font-weight: bold;
            margin-top: 15px;
            color: #555;
            font-size: 0.9em;
        }

        .item {
            margin-left: 10px;
            margin-top: 5px;
            color: #444;
            font-size: 0.85em;
        }

        .item:before {
            content: "• ";
            color: #3f51b5;
        }

        @media (max-width: 768px) {
            .columns {
                grid-template-columns: 1fr;
            }
        }

        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.8em;
            color: whitesmoke;
        }

        .bold-dark {
            font-weight: bold;
            color: #000000;
        }

        .total-agente {
            /* Estilo para o totalizador de chamados por agente */
            text-align: center;
            font-size: 1em;
            font-weight: bold;
            color: #3f51b5;
            margin-top: 10px; /* Espaçamento acima do totalizador */
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <img src="LOGO.PNG" alt="Logo" class="logo">
            <div>
                <h1>Monitor de HelpDesk</h1>
                <p id="atualizacao">Última atualização: ...</p>
            </div>
        </div>
        <div class="columns" id="dados"></div>
    </div>

    <div class="footer">
        <p>© 2025 Descarbonize Soluções<br>
            Desenvolvido por: Rodrigo Quaresma</p>
    </div>
    <script>
        async function carregarDados() {
            try {
                const response = await fetch("http://127.0.0.1:8000/chamados");
                if (!response.ok) {
                    throw new Error(`Erro na requisição: ${response.status} ${response.statusText}`);
                }
                const json = await response.json();
                const container = document.getElementById("dados");
                container.innerHTML = "";
                document.getElementById("atualizacao").innerText = "Última atualização: " + json.ultima_atualizacao;

                for (const nome in json.dados) {
                    const col = document.createElement("div");
                    col.className = "col";
                    const titulo = document.createElement("h2");
                    titulo.innerText = nome;
                    col.appendChild(titulo);

                    let totalAgente = 0; // Inicializa o contador para cada agente

                    const faixas = json.dados[nome];
                    for (const faixa in faixas) {
                        const [inicio, fim] = faixa.split("-");
                        const hora = document.createElement("div");
                        hora.className = "hora";
                        hora.innerText = `${inicio.padStart(2, '0')}:00h às ${fim.padStart(2, '0')}:00h`;
                        col.appendChild(hora);

                        if (Array.isArray(faixas[faixa])) {
                            faixas[faixa].forEach(chamado => {
                                const item = document.createElement("div");
                                item.className = "item";
                                const reporterNome = chamado.reporter || "N/A";
                                const resumo = chamado.resumo || "N/A";
                                item.innerHTML = `HDA - <span class="bold-dark">${chamado.chave.replace("HDA-", "")}</span> - ${resumo} [<span class="bold-dark">${reporterNome}</span>]`;
                                col.appendChild(item);
                                totalAgente++; // Incrementa o contador para cada chamado do agente
                            });
                        } else {
                            console.error(`faixas[faixa] não é um array para o colaborador ${nome} e faixa ${faixa}`, faixas[faixa]);
                            const erroDiv = document.createElement("div");
                            erroDiv.className = "item";
                            erroDiv.innerText = `Erro: Dados de chamados inválidos para ${nome} - ${faixa}`;
                            col.appendChild(erroDiv);
                        }
                    }
                    // Adiciona o elemento para exibir o total de chamados do agente
                    const totalAgenteDiv = document.createElement("div");
                    totalAgenteDiv.className = "total-agente";
                    totalAgenteDiv.innerText = `Resolvidos: ${totalAgente}`;
                    col.appendChild(totalAgenteDiv);

                    container.appendChild(col);
                }
            } catch (error) {
                console.error("Erro ao carregar dados:", error);
                const erroDiv = document.createElement("div");
                erroDiv.style.color = "red";
                erroDiv.innerText = "Ocorreu um erro ao carregar os dados. Por favor, verifique o console para mais detalhes.";
                document.getElementById("dados").appendChild(erroDiv);
            }
        }

        carregarDados();
        setInterval(carregarDados, 60000);
    </script>
</body>

</html>
