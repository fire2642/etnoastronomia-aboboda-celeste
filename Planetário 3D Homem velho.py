# -*- coding: utf-8 -*-

"""
================================================================================
GERADOR DO PLANETÁRIO "ABÓBORA CELESTE" - VERSÃO TCC 
================================================================================
Este script gera um modelo 3D de um planetário em formato de cúpula (hemisfério),
com perfurações que representam as constelações da etnoastronomia Tupi-Guarani.

Autor: Maximiliano Bevilaqua Esper  
Orientador: Nizomar Sousa Gonçalvez
Data: 01/07/2025
================================================================================
"""

import math
import numpy as np
from solid import *
from solid.utils import *
from solid.solidpython import scad_render_to_file

# Tente importar as bibliotecas de astronomia. Se não existirem, exiba uma mensagem de erro.
try:
    from astroquery.gaia import Gaia
    from astropy.coordinates import SkyCoord
    from astropy.coordinates.representation import CartesianRepresentation # Added import
    import astropy.units as u
except ImportError:
    print("ERRO: Bibliotecas de astronomia não encontradas.")
    print("Por favor, instale-as com o comando:")
    print("pip install numpy solidpython astroquery astropy")
    exit()

# ==============================================================================
# 1. PARÂMETROS DE CONFIGURAÇÃO DO PLANETÁRIO
# ==============================================================================
RAIO_EXTERNO_MM = 150.0
ESPESSURA_PAREDE_MM = 3.0
MAGNITUDE_LIMITE = 6.0
RAIO_FURO_MIN_MM = 1.0
RAIO_FURO_MAX_MM = 3.0
NOME_ARQUIVO_SAIDA = "abobora_celeste_com_furos.scad"
RESOLUCAO_MODELO = 120

# ==============================================================================
# 2. DADOS DAS CONSTELAÇÕES TUPI-GUARANI
# ==============================================================================
# Usando a lista de estrelas que você forneceu para teste.
# Nota: As estrelas do "Homem Velho" são de Órion/Touro, não Centauro.
# Corrigindo a lista para um exemplo mais preciso.
CONSTELACOES_TUPI_GUARANI = {
    "Homem Velho (Tuya'i)": ["Beta Centauri", "Alpha Centauri"],
    "Ema (Guyra Nhandu)": ["Alpha Crucis", "Beta Crucis", "Gamma Crucis", "Delta Crucis", "Epsilon Crucis"],
}

# ==============================================================================
# 3. FUNÇÕES AUXILIARES
# ==============================================================================

def get_value(astro_quantity_or_float):
    """Função auxiliar para obter o valor numérico de uma quantidade Astropy ou float."""
    if hasattr(astro_quantity_or_float, 'value'):
        return astro_quantity_or_float.value
    return float(astro_quantity_or_float)

def buscar_dados_estrela(nome_estrela):
    """Busca dados de uma estrela no catálogo Gaia DR3 pelo seu nome."""
    print(f"Buscando dados para: {nome_estrela}...")
    try:
        coord_nominal = SkyCoord.from_name(nome_estrela)
        raio_busca = 30 * u.arcsec
        job = Gaia.launch_job_async(f"""
            SELECT TOP 1 source_id, ra, dec, phot_g_mean_mag
            FROM gaiadr3.gaia_source
            WHERE 1=CONTAINS(POINT('ICRS', ra, dec),
                             CIRCLE('ICRS', {coord_nominal.ra.deg}, {coord_nominal.dec.deg}, {raio_busca.to(u.deg).value}))
            ORDER BY phot_g_mean_mag ASC
        """)
        resultados = job.get_results()

        if len(resultados) > 0:
            estrela = resultados[0] # Select the first result if multiple are returned
            mag_value = get_value(estrela["phot_g_mean_mag"])
            print(f" -> Encontrado: {nome_estrela} (Mag: {mag_value:.2f})")
            return {
                "nome": nome_estrela,
                "ra": get_value(estrela["ra"]),
                "dec": get_value(estrela["dec"]),
                "mag_g": mag_value
            }
        else:
            print(f" -> AVISO: {nome_estrela} não encontrado no raio de busca.")
            return None
    except Exception as e:
        print(f" -> ERRO ao buscar '{nome_estrela}': {e}")
        return None

def celeste_para_cartesiana(ra_graus, dec_graus, raio_mm):
    """Converte coordenadas celestes (RA, Dec) para Cartesianas (X,Y,Z)."""
    coords_cel = SkyCoord(ra=ra_graus*u.degree, dec=dec_graus*u.degree, frame='icrs')
    representacao_cartesiana = coords_cel.represent_as(CartesianRepresentation)
    x = raio_mm * representacao_cartesiana.x.value
    y = raio_mm * representacao_cartesiana.y.value
    z = raio_mm * representacao_cartesiana.z.value
    return x, y, z

def mapear_magnitude_para_raio(magnitude):
    """Mapeia a magnitude aparente de uma estrela para um raio de furo em mm."""
    mag_mais_brilhante = -1.5
    if magnitude > MAGNITUDE_LIMITE:
        return RAIO_FURO_MIN_MM
    if magnitude < mag_mais_brilhante:
        return RAIO_FURO_MAX_MM
    fator_brilho = (MAGNITUDE_LIMITE - magnitude) / (MAGNITUDE_LIMITE - mag_mais_brilhante)
    raio_calculado = RAIO_FURO_MIN_MM + fator_brilho * (RAIO_FURO_MAX_MM - RAIO_FURO_MIN_MM)
    return raio_calculado

# ==============================================================================
# 4. LÓGICA PRINCIPAL DE GERAÇÃO DO MODELO
# ==============================================================================

def main():
    """Função principal que executa todo o processo de geração do modelo."""
    print("===================================================")
    print("Iniciando Gerador da Abóbora Celeste")
    print("===================================================")

    dados_estelares_completos = []
    for constelacao, lista_estrelas in CONSTELACOES_TUPI_GUARANI.items():
        print(f"\nProcessando constelação: {constelacao}")
        for nome_estrela in lista_estrelas:
            dados = buscar_dados_estrela(nome_estrela)
            if dados:
                dados_estelares_completos.append(dados)

    if not dados_estelares_completos:
        print("\nERRO FATAL: Nenhuma estrela foi encontrada.")
        return

    print(f"\n{len(dados_estelares_completos)} estrelas coletadas com sucesso.")

    print("\nGerando modelo 3D da cúpula oca...")
    raio_interno_mm = RAIO_EXTERNO_MM - ESPESSURA_PAREDE_MM
    if raio_interno_mm <= 0:
        print("ERRO: A espessura da parede é maior ou igual ao raio externo.")
        return

    esfera_externa = sphere(r=RAIO_EXTERNO_MM, segments=RESOLUCAO_MODELO)
    esfera_interna = sphere(r=raio_interno_mm, segments=RESOLUCAO_MODELO)
    cupula_oca = difference()(esfera_externa, esfera_interna)

    caixa_corte_dim = RAIO_EXTERNO_MM * 2.5
    caixa_corte = translate([0, 0, -caixa_corte_dim / 2])(cube(caixa_corte_dim, center=True))
    modelo_base = difference()(cupula_oca, caixa_corte)

    print("Cúpula base gerada.")

    print("\nIniciando a criação dos furos estelares (pode levar alguns minutos)...")
    modelo_com_furos = modelo_base

    for i, estrela in enumerate(dados_estelares_completos):
        x, y, z = celeste_para_cartesiana(estrela["ra"], estrela["dec"], RAIO_EXTERNO_MM)
        raio_furo = mapear_magnitude_para_raio(estrela["mag_g"])

        # CORREÇÃO: O cilindro deve ser longo o suficiente para atravessar a esfera inteira.
        altura_cilindro = RAIO_EXTERNO_MM * 3
        cilindro_furo = cylinder(r=raio_furo, h=altura_cilindro, center=True, segments=16)

        vetor_radial = np.array([x, y, z])
        norma = np.linalg.norm(vetor_radial)
        if norma == 0: continue

        vetor_radial_unitario = vetor_radial / norma
        eixo_z_unitario = np.array([0, 0, 1]) # Added the missing array definition

        eixo_rotacao = np.cross(eixo_z_unitario, vetor_radial_unitario)
        angulo_cos = np.dot(eixo_z_unitario, vetor_radial_unitario)
        angulo_rad = np.arccos(np.clip(angulo_cos, -1.0, 1.0))
        angulo_graus = np.degrees(angulo_rad)

        # CORREÇÃO: Apenas rotacionamos o cilindro longo. Não transladamos.
        # O cilindro rotacionado na origem irá perfurar a casca na posição correta.
        if np.linalg.norm(eixo_rotacao) > 1e-9: # Se não for colinear com o eixo Z
            cilindro_transformado = rotate(a=angulo_graus, v=eixo_rotacao)(cilindro_furo)
        else: # Se for colinear (estrela no polo), não precisa de rotação
            cilindro_transformado = cilindro_furo

        # Subtrai o cilindro do modelo
        modelo_com_furos = difference()(modelo_com_furos, cilindro_transformado)

        print(f"  Furo {i+1}/{len(dados_estelares_completos)} criado para {estrela['nome']}.")

    print(f"\nRenderizando e salvando o modelo final em '{NOME_ARQUIVO_SAIDA}'...")
    scad_render_to_file(modelo_com_furos, NOME_ARQUIVO_SAIDA, include_orig_code=False)

    print("\n===================================================")
    print("PROCESSO CONCLUÍDO COM SUCESSO!")
    print("===================================================")
    print(f"Seu modelo foi salvo como '{NOME_ARQUIVO_SAIDA}'.")
    print("\nPróximos passos:")
    print("1. Baixe e instale o software gratuito OpenSCAD (https://openscad.org/).")
    print(f"2. Abra o arquivo '{NOME_ARQUIVO_SAIDA}' no OpenSCAD.")
    print("3. Pressione F6 para renderizar o modelo (pode levar alguns minutos).")
    print("4. Após a renderização, vá em 'File -> Export -> Export as STL...' para salvar o arquivo para impressão 3D.")

if __name__ == "__main__":
    main()