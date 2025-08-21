
#!/usr/bin/env bash
# 3.3.3 Ensure bogus icmp responses are ignored

{
   l_output="" l_output2=""
   a_parlist=("net.ipv4.icmp_ignore_bogus_error_responses=1")
   l_ufwscf="$([ -f /etc/default/ufw ] && awk -F= '/^\s*IPT_SYSCTL=/ {print $2}' /etc/default/ufw)"
   kernel_parameter_chk()
   {  
      l_krp="$(sysctl "$l_kpname" | awk -F= '{print $2}' | xargs)" # Vérifier la configuration en cours
      if [ "$l_krp" = "$l_kpvalue" ]; alors
         l_output="$l_output\n - \"$l_kpname\" est correctement réglé sur \"$l_krp\" dans la configuration en cours"
      else
         l_output2="$l_output2\n - \"$l_kpname\" est incorrectement réglé sur \"$l_krp\" dans la configuration en cours et devrait avoir la valeur : \"$l_kpvalue\""
      fi
      unset A_out; declare -A A_out # Vérifier les paramètres dans les fichiers de configuration
      while read -r l_out; do
         if [ -n "$l_out" ]; alors
            if [[ $l_out =~ ^\s*# ]]; alors
               l_file="${l_out//# /}"
            else
               l_kpar="$(awk -F= '{print $1}' <<< "$l_out" | xargs)"
               [ "$l_kpar" = "$l_kpname" ] && A_out+=(["$l_kpar"]="$l_file")
            fi
         fi
      done < <(/usr/lib/systemd/systemd-sysctl --cat-config | grep -Po '^\h*([^#\n\r]+|#\h*\/[^#\n\r\h]+\.conf\b)')
      if [ -n "$l_ufwscf" ]; alors # Tenir compte des systèmes avec UFW (Non couvert par systemd-sysctl --cat-config)
         l_kpar="$(grep -Po "^\h*$l_kpname\b" "$l_ufwscf" | xargs)"
         l_kpar="${l_kpar//\//.}"
         [ "$l_kpar" = "$l_kpname" ] && A_out+=(["$l_kpar"]="$l_ufwscf")
      fi
      if (( ${#A_out[@]} > 0 )); alors # Évaluer les sorties des fichiers et générer la sortie
         while IFS="=" read -r l_fkpname l_fkpvalue; do
            l_fkpname="${l_fkpname// /}"; l_fkpvalue="${l_fkpvalue// /}"
            if [ "$l_fkpvalue" = "$l_kpvalue" ]; alors
               l_output="$l_output\n - \"$l_kpname\" est correctement réglé sur \"$l_fkpvalue\" dans \"$(printf '%s' "${A_out[@]}")\"\n"
            else
               l_output2="$l_output2\n - \"$l_kpname\" est incorrectement réglé sur \"$l_fkpvalue\" dans \"$(printf '%s' "${A_out[@]}")\" et devrait avoir la valeur : \"$l_kpvalue\"\n"
            fi
         done < <(grep -Po -- "^\h*$l_kpname\h*=\h*\H+" "${A_out[@]}")
      else
         l_output2="$l_output2\n - \"$l_kpname\" n'est pas réglé dans un fichier inclus\n   ** Note: \"$l_kpname\" peut être réglé dans un fichier ignoré par la procédure de chargement **\n"
      fi
   }
   while IFS="=" read -r l_kpname l_kpvalue; do # Évaluer et vérifier les paramètres
      l_kpname="${l_kpname// /}"; l_kpvalue="${l_kpvalue// /}"
      kernel_parameter_chk
   done < <(printf '%s\n' "${a_parlist[@]}")
   if [ -z "$l_output2" ]; alors # Fournir la sortie des vérifications
      echo -e "\n- Résultat de l'audit:\n  ** PASS **\n$l_output\n"
   else
      echo -e "\n- Résultat de l'audit:\n  ** FAIL **\n - Raisons de l'échec de l'audit:\n$l_output2\n"
      [ -n "$l_output" ] && echo -e "\n- Correctement réglé:\n$l_output\n"
   fi
}
