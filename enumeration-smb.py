import os
import smbclient
import subprocess
from sys import argv


def telechargement_et_test_upload_serveur_SMB(connexion_partage_SMB, serveur_SMB_distant, nom_partage):
    try:
        liste_dossier_partage_smb = ["/"]
        for dossier in liste_dossier_partage_smb:
            for element in (connexion_partage_SMB.listdir(dossier)):
                if (connexion_partage_SMB.exists(dossier + element + "/")) == True:
                    liste_dossier_partage_smb.append(dossier + element + "/")
        try:
            os.mkdir(serveur_SMB_distant + "-SMB/" + nom_partage)
        except:
            print("Le dossier %s-SMB/%s existe déjà" % (serveur_SMB_distant, nom_partage))

        for dossier in liste_dossier_partage_smb:
            if dossier != "/":
                try:
                    os.mkdir(serveur_SMB_distant + "-SMB/" + nom_partage + "/" + dossier)
                except:
                    print("Le dossier %s-SMB/%s/%s existe déjà" % (serveur_SMB_distant, nom_partage, dossier))

            # Test Upload de Dossier
            try:
                connexion_partage_SMB.upload("test_upload_SMB.txt", dossier + "/test_upload_SMB.txt")
                print("Upload de fichier réussi dans le dossier %s du partage SMB %s du serveur %s ! " % (dossier, nom_partage,serveur_SMB_distant))
            except:
                print("Impossible d'envoyer un fichier dans le dossier %s du partage SMB %s du serveur %s" % (dossier, nom_partage,serveur_SMB_distant))

            for element in (connexion_partage_SMB.listdir(dossier)):
                try:
                    if dossier != "/":
                        connexion_partage_SMB.download(dossier + element,
                                                       serveur_SMB_distant + "-SMB/" + nom_partage + "/" + dossier + "/" + element)
                    else:
                        connexion_partage_SMB.download(dossier + element,
                                                       serveur_SMB_distant + "-SMB/" + nom_partage + "/" + element)
                except smbclient.SambaClientError:
                    print("Téléchargement du dossier %s depuis le serveur SMB %s en cours" % (
                    element, serveur_SMB_distant))

        is_function_suceeded = True
        return is_function_suceeded
    except smbclient.SambaClientError:
        is_function_suceeded = False
        return is_function_suceeded


def main():

    if len(argv) == 2 :
        serveur_SMB = argv[1]
        username_SMB = ""
        password_SMB = ""
    elif len(argv) == 4 :
        serveur_SMB = argv[1]
        username_SMB = argv[2]
        password_SMB = argv[3]
    else:
        print ("Exécution du script : python3 enumeration-smb.py serveur_SMB [ usernameSMB passwordSMB]")
        exit(0)

    # LISTING DES PARTAGES SMB
    if username_SMB == "" :
        message_smbclient = subprocess.getstatusoutput("/usr/bin/smbclient -L " + serveur_SMB + " -N")
    else:
        #Creation du fichier authfile
        fichier_authfile = open("authfileSMB-" + serveur_SMB,"w")
        fichier_authfile.write("username = " + username_SMB + "\n")
        fichier_authfile.write("password = " + password_SMB + "\n")
        fichier_authfile.close()
        message_smbclient = subprocess.getstatusoutput("/usr/bin/smbclient -L " + serveur_SMB + " -A authfileSMB-" + serveur_SMB  )
        os.remove("authfileSMB-" + serveur_SMB)

    if message_smbclient[0] == 1:
        print("Impossible d'afficher la liste des partages SMB du serveur %s sans identifiant" % serveur_SMB)
        exit(0)

    sortie_smbclient = message_smbclient[1].split("\n")

    del sortie_smbclient[0:3]

    if username_SMB == "" :
        print("Voici la liste des partages SMB du serveur %s visibles sans identifiant :" % serveur_SMB)
    else :
        print("Voici la liste des partages SMB  du serveur %s visibles avec le compte %s : " % (serveur_SMB,username_SMB))

    liste_Partage_SMB = []

    for ligne_sortie_smbclient in sortie_smbclient:
        if "Disk" in ligne_sortie_smbclient:
            longueur_nom_partage_SMB = ligne_sortie_smbclient.find(" ")
            liste_Partage_SMB.append(ligne_sortie_smbclient[1:longueur_nom_partage_SMB])

    print(liste_Partage_SMB)

    try:
        os.mkdir(serveur_SMB + "-SMB")
    except:
        print("Le dossier %s-SMB existe déjà" % serveur_SMB)

    fichier_test_upload = open("test_upload_SMB.txt", "w")
    fichier_test_upload.write("Test upload de fichier vers serveur SMB")
    fichier_test_upload.close()

    if username_SMB == "" :
    # Connexion aux différents partages SMB sans identifiant
        for partage_SMB in liste_Partage_SMB:

            connexion_smb = smbclient.SambaClient(server=serveur_SMB, share=partage_SMB, username="anonymous", password="")
            is_function_succeeded = telechargement_et_test_upload_serveur_SMB(connexion_smb, serveur_SMB, partage_SMB)

            if is_function_succeeded == False:

                connexion_smb = smbclient.SambaClient(server=serveur_SMB, share=partage_SMB, username="", password="")
                is_function_succeeded = telechargement_et_test_upload_serveur_SMB(connexion_smb, serveur_SMB, partage_SMB)

                if is_function_succeeded == False:
                    print("Impossible de se connecter au partage SMB %s du serveur %s sans identifiant" % (partage_SMB,serveur_SMB))

    else :
    # Connexion aux différents partages SMB avec identifiant
        for partage_SMB in liste_Partage_SMB:
            connexion_smb = smbclient.SambaClient(server=serveur_SMB, share=partage_SMB, username=username_SMB, password=password_SMB)
            is_function_succeeded = telechargement_et_test_upload_serveur_SMB(connexion_smb, serveur_SMB, partage_SMB)

            if is_function_succeeded == False:
                print("Impossible de se connecter au partage SMB %s du serveur %s avec le compte %s" % (partage_SMB, serveur_SMB,username_SMB))


    print(
        "Le contenu de tous les partages SMB du serveur %s accessibles avec les identifiants données ont été téléchargés dans le dossier %s-SMB" % (
            serveur_SMB, serveur_SMB))
    os.remove("test_upload_SMB.txt")


if __name__ == "__main__":
    main()