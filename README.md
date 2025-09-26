# etnoastronomia-aboboda-celeste
# Abóbada Celeste: Planetário Tupi-Guarani de Baixo Custo

![Foto do Protótipo](foto_prototipo.jpg)  Este repositório contém o código-fonte e os modelos 3D para a fabricação do "Abóbada Celeste", um planetário de baixo custo para a divulgação da etnoastronomia Tupi-Guarani.

O projeto foi desenvolvido por Maximiliano Bevilaqua Esper como parte de seu Trabalho de Conclusão de Curso em Licenciatura em Física no IFCE.

### Artigo Científico
Este trabalho foi detalhado no artigo:
> M. B. Esper, J. C. F. Bastos, e N. S. Gonçalves, "Representação de Constelações Tupi-Guarani em um Planetário 3D de Baixo Custo", *Cadernos de Astronomia*, [Ano, Volume, Página - preencher quando publicado].

---

## Conteúdo do Repositório

* **/script_planetario.py**: Script em Python que consulta o catálogo estelar Gaia DR3 e gera parametricamente o modelo 3D.
* **/abobada_celeste.scad**: Arquivo de modelo 3D editável para uso no OpenSCAD.
* **/abobada_celeste.stl**: Arquivo final pronto para ser fatiado e impresso em uma impressora 3D.

## Como Usar

### 1. Requisitos para o Script
Para executar o script Python e gerar seus próprios modelos, você precisará das seguintes bibliotecas:
```bash
pip install numpy solidpython astroquery astropy
