import sqlite3
from os import remove
from utils import scan_for_virtual_audio_paths


class DbInterface:

    def __init__(self):
        self.db_reference = "db/cases/"

    def create_case(self,
                    case_name,
                    evidences):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        query = ("CREATE TABLE case_evidences("
                 "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "
                 "name TEXT UNIQUE NOT NULL, "
                 "files_path TEXT NOT NULL, "
                 "transcriptions TEXT NOT NULL, "
                 "last_search ,"
                 "number_of_files INTEGER"
                 ")")
        cur.execute(query)
        query = ("CREATE TABLE evidences("
                 "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "
                 "file_name NOT NULL, "
                 "evidence NOT NULL,"
                 "text TEXT,"
                 "language TEXT,"
                 "FOREIGN KEY(evidence) REFERENCES case_data(name)"
                 ")"
                 )
        cur.execute(query)
        query = ("CREATE TABLE search_result("
                 "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "
                 "file_id NOT NULL, "
                 "file_evidence NOT NULL,"
                 "word_similarity REAL,"
                 "window_similarity REAL,"
                 "average_similarity REAL,"
                 "FOREIGN KEY(file_id) REFERENCES evidences(id)"
                 "FOREIGN KEY(file_evidence) REFERENCES evidences(evdence)"
                 ")"
                 )
        cur.execute(query)
        for evidence in evidences:
            query = ("INSERT INTO case_evidences(name,files_path,transcriptions) "
                     "VALUES(?,?,?)")
            cur.execute(query, (evidence[0], evidence[1], "creating"))
        con.commit()
        con.close()

    def insert_evidence_files_path(self,
                                   case_name,
                                   evidence,
                                   files_path):
        files = scan_for_virtual_audio_paths(files_path)
        for relative_path in files:
            con = sqlite3.connect(self.db_reference + case_name + ".db")
            cur = con.cursor()
            sql = ("INSERT INTO evidences" +
                   "(file_name,evidence,text,language) "
                   "VALUES(?,?,Null,Null) ")
            cur.execute(sql, [relative_path, evidence])
            con.commit()
            con.close()

        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("UPDATE case_evidences "
               "SET number_of_files = ? "
               "WHERE name = ? ")
        cur.execute(sql, (len(files), evidence))
        con.commit()
        con.close()
        self.change_transcription_status(case_name, evidence, "todo")

    def insert_evidence(self,
                        case_name,
                        evidence,
                        path):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("INSERT INTO case_evidences(name, files_path, transcriptions) "
               "VALUES(?,?,?)")
        cur.execute(sql, [evidence, path, "creating"])

        con.commit()
        con.close()

    def change_transcription_status(self,
                                    case_name,
                                    evidence,
                                    status):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = "UPDATE case_evidences SET transcriptions = ? WHERE name = ?"
        cur.execute(sql, (status, evidence))
        con.commit()
        con.close()

    def take_files_to_transcribe_with_size(self,
                                           case_name,
                                           evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("SELECT file_name "
               "FROM evidences "
               "WHERE evidence = ? and text is NULL ")
        cur.execute(sql, [evidence])
        rows = cur.fetchall()
        sql = ("SELECT number_of_files "
               "FROM case_evidences "
               "WHERE name = ? ")
        cur.execute(sql, [evidence])
        total_size = cur.fetchone()
        results = []
        for row in rows:
            results.append(row[0])
        con.close()
        return results, len(results), int(total_size[0])  # db returns a tuple

    def take_data_for_report(self,
                             case_name,
                             evidence,
                             file_names):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        placeholders = ','.join('?' for _ in file_names)

        query = (
            f"SELECT * "
            f"FROM evidences "
            f"INNER JOIN search_result ON search_result.file_id = evidences.id "
            f"WHERE evidence = ? AND file_name IN ({placeholders})"
        )

        params = [evidence] + file_names
        cur.execute(query, params)
        rows = cur.fetchall()
        results = []
        for row in rows:
            data = {
                "file_name": row[1],
                "evidence": row[2],
                "transcription": row[3],
                "language": row[4],
                "word_similarity": row[8],
                "window_similarity": row[9],
                "average_similarity": row[10]
            }
            results.append(data)
        query2 = (f"SELECT * "
                  f"FROM case_evidences "
                  f"WHERE name = ? ")
        cur.execute(query2, [evidence])
        evidence_data = cur.fetchone()
        evidence_dict = {
            "evidence": evidence_data[1],
            "files_path": evidence_data[2],
            "transcription": evidence_data[3],
            "last_search": evidence_data[4],
            "number_of_files": evidence_data[5],
        }
        con.close()
        return evidence_dict, results

    def take_evidences_data(self,
                            case_name):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("SELECT * "
               "FROM case_evidences")
        cur.execute(sql)
        rows = cur.fetchall()
        results = []
        for row in rows:
            data = {
                "evidence": row[1],
                "files_path": row[2],
                "transcriptions": row[3],
                "last_search": row[4]
            }
            results.append(data)
        con.close()
        return results

    def delete_case(self,
                    case_name):
        remove(self.db_reference + case_name + ".db")

    def delete_evidence(self,
                        case_name,
                        evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = "DELETE FROM evidences WHERE evidence = ?"
        cur.execute(sql, [evidence])
        sql = "DELETE FROM case_evidences WHERE name = ?"
        cur.execute(sql, [evidence])
        sql = "DELETE FROM search_result WHERE file_evidence = ?"
        cur.execute(sql, [evidence])
        con.commit()
        con.close()

    def insert_transcription(self,
                             case_name,
                             evidence,
                             data):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = "UPDATE evidences SET text = ? , language = ?  WHERE file_name = ? and evidence = ?"
        cur.execute(sql, [data[1],
                          data[2],
                          data[0],
                          evidence])
        con.commit()
        con.close()

    def take_analyzed_file_names(self,
                                 case_name,
                                 evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("SELECT file_name FROM evidences WHERE evidence = '" + evidence + "'")
        cur.execute(sql)
        rows = cur.fetchall()
        results = []
        for row in rows:
            results.append(row[0])
        con.close()
        return results

    def take_data(self,
                  case_name,
                  evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("SELECT * FROM evidences WHERE evidence = '" + evidence + "'")
        cur.execute(sql)
        rows = cur.fetchall()
        results = []
        for row in rows:
            data = {
                "id": row[0],
                "file_name": row[1],
                "evidences": row[2],
                "text": row[3],
                "language": row[4],
                "window": row[5],
                "word": row[6],
                "average": row[7]
            }
            results.append(data)
        con.close()
        return results

    def take_transcribed_text(self,
                              case_name,
                              evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = "SELECT id, text, language FROM  evidences  WHERE evidence = ?"
        cur.execute(sql, [evidence])
        rows = cur.fetchall()
        if len(rows) == 0:
            return FileNotFoundError
        result = []
        for row in rows:
            data = {
                "id": row[0],
                "text": row[1],
                "language": row[2],
            }
            result.append(data)
        con.close()
        return result

    def take_text_from_id(self,
                          case_name, evidence, file_id):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("SELECT id, text, language FROM  evidences  WHERE id ='" + str(
            file_id)) + "' and evidence = '" + evidence + "'"
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) == 0:
            return FileNotFoundError
        result = []
        for row in rows:
            data = {
                "id": row[0],
                "text": row[1],
                "language": row[2],
            }
            result.append(data)
        con.close()
        return result[0]

    def insert_similarities(self,
                            case_name,
                            evidence,
                            file_id,
                            average_similarity,
                            window_similarity,
                            word_similarity):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("UPDATE search_result SET average_similarity = ?, word_similarity = ?, window_similarity = ? "
               "WHERE file_id = ? and file_evidence = ?")
        cur.execute(sql, [average_similarity, word_similarity, window_similarity, file_id, evidence])
        con.commit()
        con.close()

    def insert_average_similarity(self,
                                  case_name,
                                  evidence,
                                  file_id,
                                  average_similarity):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = "UPDATE search_result SET average_similarity = '" + str(average_similarity) + "' WHERE file_id =" + str(
            file_id) + " and file_evidence = '" + str(evidence) + "'"
        cur.execute(sql)
        con.commit()
        con.close()

    def insert_window_similarity(self,
                                 case_name,
                                 evidence,
                                 file_id,
                                 window_similarity):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = "UPDATE search_result SET window_similarity = '" + str(window_similarity) + "' WHERE file_id =" + str(
            file_id) + " and file_evidence = '" + str(evidence) + "'"
        cur.execute(sql)
        con.commit()
        con.close()

    def insert_word_similarity(self,
                               case_name,
                               evidence,
                               file_id,
                               word_similarity):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = "UPDATE search_result SET word_similarity = '" + str(word_similarity) + "' WHERE file_id =" + str(
            file_id) + " and file_evidence = '" + str(evidence) + "'"
        cur.execute(sql)
        con.commit()
        con.close()

    def get_last_search(self,
                        case_name,
                        evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("SELECT last_search "
               "FROM case_evidences "
               "WHERE name = '" + evidence +
               "' ")
        cur.execute(sql)
        row = cur.fetchone()
        return row[0]

    def put_last_search(self,
                        case_name,
                        evidence,
                        last_search):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = "UPDATE case_evidences SET last_search = '" + str(last_search) + "' WHERE name = '" + str(evidence) + "'"
        cur.execute(sql)
        con.commit()
        con.close()

    def remove_current_search(self,
                              case_name,
                              evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("DELETE FROM search_result "
               "WHERE file_evidence ='" + evidence + "'")
        cur.execute(sql)
        sql = "UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='search_result';"
        cur.execute(sql)
        con.commit()
        con.close()

    def get_current_average_similarity_search(self,
                                              case_name,
                                              evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("SELECT file_name, text, average_similarity, language "
               "FROM evidences "
               "INNER JOIN search_result ON evidences.id = search_result.file_id "
               "WHERE evidences.evidence = '" + evidence +
               "' "
               "ORDER BY average_similarity DESC")
        cur.execute(sql)
        results = []
        no_language_available_results = []
        rows = cur.fetchall()
        for row in rows:

            data = {
                "file_name": row[0],
                "text": row[1],
                "similarity": row[2],
                "language": row[3]
            }
            if data["similarity"] == "No data":
                no_language_available_results.append(data)
            else:
                results.append(data)
        con.commit()
        con.close()
        return results + no_language_available_results

    def get_current_word_similarity_search(self,
                                           case_name,
                                           evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("SELECT file_name, text, word_similarity, language "
               "FROM evidences "
               "INNER JOIN search_result ON evidences.id = search_result.file_id "
               "WHERE evidences.evidence = '" + evidence +
               "' "
               "ORDER BY word_similarity DESC")
        cur.execute(sql)
        results = []
        no_language_available_results = []
        rows = cur.fetchall()
        for row in rows:

            data = {
                "file_name": row[0],
                "text": row[1],
                "similarity": row[2],
                "language": row[3]
            }
            if data["similarity"] == "No data":
                no_language_available_results.append(data)
            else:
                results.append(data)
        con.commit()
        con.close()
        return results + no_language_available_results

    def get_current_window_similarity_search(self,
                                             case_name,
                                             evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("SELECT file_name, text, window_similarity, language "
               "FROM evidences "
               "INNER JOIN search_result ON evidences.id = search_result.file_id "
               "WHERE evidences.evidence = '" + evidence +
               "' "
               "ORDER BY window_similarity DESC")
        cur.execute(sql)
        results = []
        no_language_available_results = []
        rows = cur.fetchall()
        for row in rows:

            data = {
                "file_name": row[0],
                "text": row[1],
                "similarity": row[2],
                "language": row[3]
            }
            if data["similarity"] == "No data":
                no_language_available_results.append(data)
            else:
                results.append(data)
        con.commit()
        con.close()
        return results + no_language_available_results

    def insert_file_id_and_evidence(self,
                                    case_name,
                                    file_id, evidence):
        con = sqlite3.connect(self.db_reference + case_name + ".db")
        cur = con.cursor()
        sql = ("INSERT INTO "
               "search_result(file_id, file_evidence)"
               "VALUES(?,?) ")
        cur.execute(sql, [file_id, evidence])
        con.commit()
        con.close()
