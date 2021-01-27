import json
import os
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
import design
import random
from PyQt5.QtGui import QColor
import pymongo


colors = ['#93ffaa', '#ffbbc7']

class Loader(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.db = pymongo.MongoClient('mongodb://developer:Smidle098adm!@sm-dev-svb.smiddle.lab:27017')['devsvb']['nluSmiddle']
        #print(self.db.find_one({'call_id': "ac22767c-4632-49fb-925a-b8be398ad7cf"}))
        self.dialogues_checked = []
        self.setupUi(self)
        self.check_working_directory()
        self.init_ui()
        self.load_entity_types_and_synonims()
        self.phrases_config = {}
        self.dialogue_index = -1
        self.last_call_id = None
        self.current_call_id = None
        self.load_next_dump()
        self.s_phrases = {}

    def init_ui(self):
        self.next_dialogue_btn.clicked.connect(self.load_next_dump)
        self.prev_dialogue_btn.clicked.connect(self.load_prev_dump)
        self.phrases_list_wid.itemClicked.connect(self.on_phrase_clicked)
        self.save_phrase_btn.clicked.connect(self.save_phrase)
        #self.phrase_edit.isReadOnly = True
        self.end_phrase.isReadOnly = True
        self.phrase_edit.selectionChanged.connect(self.on_text_selected)
        self.object_type_select.currentTextChanged.connect(self.on_object_type_selected)
        self.domain_selector.currentTextChanged.connect(self.on_domain_chosen)
        self.intents_selector.currentTextChanged.connect(self.on_intent_chosen)
        self.synonim_to_object_select.currentTextChanged.connect(self.on_synonim_to_selected)

    def on_phrase_clicked(self, item_widget):
        phrase = item_widget.text()
        saved_config = self.phrases_config.get(phrase.replace('Вы:', '').strip())
        if 'Вы:' not in phrase:
            self.phrase_edit.clear()
            self.end_phrase.clear()
            self.domain_selector.clear()
            self.intents_selector.clear()
            self.object_type_select.clear()
            self.synonim_to_object_select.clear()
        elif not saved_config:
            self.domain_selector.clear()
            self.intents_selector.clear()
            phrase = phrase.replace('Вы:', '').strip()
            self.phrase_edit.setText(phrase)
            self.end_phrase.setText(phrase)
            self.object_type_select.clear()
            self.synonim_to_object_select.clear()
            self.init_domains_intents()
        elif saved_config:
            self.domain_selector.clear()
            self.intents_selector.clear()
            phrase = phrase.replace('Вы:', '').strip()
            self.phrase_edit.setText(phrase)
            self.end_phrase.setText(saved_config['end_phrase'])
            self.object_type_select.clear()
            self.synonim_to_object_select.clear()
            self.init_domains_intents(saved_config)

    def load_prev_dump(self):
        #self.save_phrase()
        self.domain_selector.clear()
        self.intents_selector.clear()
        self.synonim_to_object_select.clear()
        #print('Next btn clicked')
        self.phrase_edit.clear()
        self.end_phrase.clear()
        self.phrases_list_wid.clear()
        self.object_type_select.clear()
        self.phrases_config = {}
        if self.last_call_id:
            dump = self.db.find_one({'call_id': self.last_call_id})
            if dump:
                self.dump_name_lbl.setText(dump)
                #print(dump)
                with open(os.path.join(self.path, dump)) as f:
                    dialogue = json.loads(f.read())
                    for transaction in dialogue['history'][::-1]:
                        self.phrases_list_wid.addItem('Вы: ' + transaction['request']['text'])
                        try:
                            self.phrases_list_wid.addItem('--- ' + transaction['directives'][0]['payload']['text'])
                        except:
                            pass
            else:
                self.dump_name_lbl.setText('')
        else:
            self.dump_name_lbl.setText('')

    def load_next_dump(self):
        #self.save_phrase()
        self.domain_selector.clear()
        self.intents_selector.clear()
        self.synonim_to_object_select.clear()
        #print('Next btn clicked')
        self.phrase_edit.clear()
        self.end_phrase.clear()
        self.phrases_list_wid.clear()
        self.object_type_select.clear()
        self.phrases_config = {}
        dump = self.db.find_one({'processed': False, 'incorrect_dialog': True})
        if dump:
            if self.current_call_id:
                self.last_call_id = self.current_call_id
            self.current_call_id = dump['call_id']
            self.dump_name_lbl.setText(dump['call_id'])
            #print(dump)
            #print(self.path, dump)
            for transaction in dump['dialog']['history'][::-1]:
                #print(transaction['request']['text'])
                #print(transaction['directives'][0]['payload']['text'])
                self.phrases_list_wid.addItem('Вы: ' + transaction['request']['text'])

                try:
                    self.phrases_list_wid.addItem('--- ' + transaction['directives'][0]['payload']['text'])
                except:
                    pass
        else:
            self.dump_name_lbl.setText('')
        #print('Finished')

    def check_working_directory(self):
        self.path = os.getcwd()
        try:
            dir_list = os.listdir(self.path)
        except:
            dir_list = []
        if 'domains' not in dir_list:
            QtWidgets.QMessageBox.about(self, "Ошибка", "Не нашел нужные файлы. Откройте программу из главной папки проекта")
            sys.exit(1)
        self.domains_path = os.path.join(self.path, 'domains')
        try:
            os.listdir(self.domains_path)
        except:
            QtWidgets.QMessageBox.about(self, "Ошибка", "Не нашел нужные файлы. Откройте программу из главной папки проекта")
            sys.exit(1)

    def on_intent_chosen(self, intent):
        if intent == '<Не выбрано>' or not intent:
            return
        #print('Updating phrase')
        self.update_phrase()

    def init_domains_intents(self, saved_config=None):
        try:
            self.domains
        except:
            self.domains = self.get_domains_intents()
        #print(self.domains)
        self.domain_selector.clear()
        domains_list = list(self.domains.keys())
        self.domain_selector.addItem('<Не выбрано>')
        self.domain_selector.addItems(domains_list)
        if not saved_config:
            if len(domains_list) == 1:
                self.domain_selector.setCurrentIndex(1)
                self.on_domain_chosen(domains_list[0])
        else:
            domain_index = self.domain_selector.findText(saved_config['domain'])
            #print('Domain index:', domain_index)
            if domain_index == -1:
                if len(domains_list) == 1:
                    self.domain_selector.setCurrentIndex(1)
                    self.on_domain_chosen(domains_list[0])
                return
            self.domain_selector.setCurrentIndex(domain_index)
            intent_index = self.intents_selector.findText(saved_config['intent'])
            #print('Intent index:', intent_index)
            if intent_index == -1:
                return
            self.intents_selector.setCurrentIndex(intent_index)

    def on_domain_chosen(self, domain):
        self.intents_selector.clear()
        #print(domain)
        if domain == '<Не выбрано>' or not domain:
            return
        if not domain:
            return
        intents = self.domains[domain]
        self.intents_selector.addItem('<Не выбрано>')
        self.intents_selector.addItems(intents)

    def is_selected_text_inside_quotes(self, full_text, selected_text):
        is_quote_opened = False
        for i in range(len(full_text)):
            char = full_text[i]
            if char == '{':
                is_quote_opened = True
            elif char == '}':
                is_quote_opened = False
            text_left = full_text[i:]
            if is_quote_opened and selected_text in text_left[:text_left.index('}')]:
                return True
        return False

    def on_synonim_to_selected(self, synonim_to):
        selected_text = self.phrase_edit.textCursor().selectedText()
        if not selected_text:
            return
        object_type = self.object_type_select.currentText()
        if object_type == '<Не выбрано>' or not object_type:
            return
        if synonim_to != '<Не выбрано>' and synonim_to:
            #print('update phrase')
            self.update_phrase()
            #print(self.phrases_config)

    def on_object_type_selected(self, object_type):
        #print(self.phrases_config)
        selected_text = self.phrase_edit.textCursor().selectedText()
        #print(selected_text)
        if not selected_text:
            return
        if object_type == '<Не выбрано>' or not object_type:
            self.synonim_to_object_select.clear()
            current_phrase = self.end_phrase.toPlainText()
            if '{' + selected_text + '|' in current_phrase:
                #print('Found:', '{' + selected_text, 'in:', current_phrase)
                text_to_replace = current_phrase[current_phrase.index('{' + selected_text):]
                text_to_replace = text_to_replace[:text_to_replace.index('}')+1]
                new_phrase = current_phrase.replace(text_to_replace, selected_text)
                self.end_phrase.setText(new_phrase)
                self.update_phrase()
            return
        old_end_phrase = self.end_phrase.toPlainText()
        if '{' in selected_text:
            self.synonim_to_object_select.clear()
            return
        elif self.is_selected_text_inside_quotes(old_end_phrase, selected_text):
            #print('Selected inside quotes')
            phrase = self.phrase_edit.toPlainText()

            self.synonim_to_object_select.clear()
            self.synonim_to_object_select.addItem('<Не выбрано>')
            entities = []
            for ent in self.all_entities[object_type]['entities']:
                entities.append(ent['cname'])
            self.synonim_to_object_select.addItems(entities)
            phrase_orig = self.phrase_edit.toPlainText()
            if phrase_orig in self.phrases_config:
                #print(self.phrases_config[phrase_orig])
                for i in range(len(self.phrases_config[phrase_orig]['synonims'])):
                    syn_obj = self.phrases_config[phrase_orig]['synonims'][i]
                    #print(syn_obj['synonim'], selected_text)
                    if syn_obj['synonim'] == selected_text:
                        syn_index = self.synonim_to_object_select.findText(syn_obj['synonim_to'])
                        if syn_index == -1:
                            #print('Synonim not found')
                            continue
                        self.synonim_to_object_select.setCurrentIndex(syn_index)

            current_phrase = self.end_phrase.toPlainText()
            text_to_replace = current_phrase[current_phrase.index('{' + selected_text):]
            text_to_replace = text_to_replace[:text_to_replace.index('}')+1]
            new_text = '{' + selected_text + '|' + object_type + '}'
            new_phrase = current_phrase.replace(text_to_replace, new_text)
            self.end_phrase.setText(new_phrase)
        elif '{' not in old_end_phrase:
            new_text = '{' + selected_text + '|' + object_type + '}'

            self.synonim_to_object_select.clear()
            self.synonim_to_object_select.addItem('<Не выбрано>')
            entities = []
            for ent in self.all_entities[object_type]['entities']:
                entities.append(ent['cname'])
            self.synonim_to_object_select.addItems(entities)
            phrase_orig = self.phrase_edit.toPlainText()
            if phrase_orig in self.phrases_config:
                #print(self.phrases_config[phrase_orig])
                for i in range(len(self.phrases_config[phrase_orig]['synonims'])):
                    syn_obj = self.phrases_config[phrase_orig]['synonims'][i]
                    #print(syn_obj['synonim'], selected_text)
                    if syn_obj['synonim'] == selected_text:
                        syn_index = self.synonim_to_object_select.findText(syn_obj['synonim_to'])
                        if syn_index == -1:
                            #print('Synonim not found')
                            continue
                        self.synonim_to_object_select.setCurrentIndex(syn_index)

            end_phrase = phrase_orig.replace(selected_text, new_text)
            self.end_phrase.setText(end_phrase)
        else:
            self.synonim_to_object_select.clear()
            self.synonim_to_object_select.addItem('<Не выбрано>')
            entities = []
            for ent in self.all_entities[object_type]['entities']:
                entities.append(ent['cname'])
            self.synonim_to_object_select.addItems(entities)
            phrase_orig = self.phrase_edit.toPlainText()
            if phrase_orig in self.phrases_config:
                #print(self.phrases_config[phrase_orig])
                for i in range(len(self.phrases_config[phrase_orig]['synonims'])):
                    syn_obj = self.phrases_config[phrase_orig]['synonims'][i]
                    #print(syn_obj['synonim'], selected_text)
                    if syn_obj['synonim'] == selected_text:
                        syn_index = self.synonim_to_object_select.findText(syn_obj['synonim_to'])
                        if syn_index == -1:
                            #print('Synonim not found')
                            continue
                        self.synonim_to_object_select.setCurrentIndex(syn_index)
            #print('Just adding obj type')
            new_text = '{' + selected_text + '|' + object_type + '}'
            phrase = old_end_phrase
            end_phrase = phrase.replace(selected_text, new_text)
            self.end_phrase.setText(end_phrase)

        self.update_phrase()

    def on_text_selected(self):
        if not self.object_type_select.count():
            self.object_type_select.clear()
            self.object_type_select.addItem('<Не выбрано>')
            self.object_type_select.addItems(self.entities)
        selected_text = self.phrase_edit.textCursor().selectedText()
        #print(selected_text)
        if not selected_text:
            self.object_type_select.setCurrentIndex(0)
            self.synonim_to_object_select.clear()
            return
        current_phrase = self.end_phrase.toPlainText()
        if '{' + selected_text + '|' in current_phrase:
            entity_type = current_phrase[current_phrase.index('{' + selected_text):]
            entity_type = entity_type[entity_type.index('|')+1: entity_type.index('}')]
            item_index = self.object_type_select.findText(entity_type)
            if item_index == -1:
                return
            self.object_type_select.setCurrentIndex(item_index)
            

    def update_phrase(self):
        current = {}
        domain = self.domain_selector.currentText()
        if not domain:
            return
        #    QtWidgets.QMessageBox.about(self, "Ошибка", "Не нашел нужные файлы. Запустите программу из главной папки проекта")
        current['domain'] = domain
        intent = self.intents_selector.currentText()
        if not intent:
            return
        current['intent'] = intent
        phrase = self.phrase_edit.toPlainText()
        end_phrase = self.end_phrase.toPlainText()
        current['end_phrase'] = end_phrase
        current['saved'] = False
        if phrase not in self.phrases_config or 'synonims' not in self.phrases_config[phrase]:
            current['synonims'] = []
        else:
            current['synonims'] = self.phrases_config[phrase]['synonims']
        ent_type = self.object_type_select.currentText()
        selected_text = self.phrase_edit.textCursor().selectedText()
        if selected_text:
            if ent_type != '<Не выбрано>' and ent_type:
                synonim_to = self.synonim_to_object_select.currentText()
                if synonim_to != '<Не выбрано>' and synonim_to:
                    for i in range(len(current['synonims'])):
                        syn_obj = current['synonims'][i]
                        if syn_obj['synonim'] == selected_text:
                            current['synonims'].pop(i)
                            break
                    syn_obj = {}
                    syn_obj['synonim_to'] = synonim_to
                    syn_obj['ent_type'] = ent_type
                    syn_obj['synonim'] = selected_text
                    current['synonims'].append(syn_obj)
        #print(current)
        self.phrases_config[phrase] = current

    def save_phrase(self):
        self.update_phrase()
        self.save_log_list.clear()
        for phrase, config in self.phrases_config.items():
            if config['saved']:
                continue
            if config['domain'] == '<Не выбрано>' or not config['domain']:
                QtWidgets.QMessageBox.about(self, "Ошибка", "Для фразы: <" + phrase + "> не выбран домен. Не могу сохранить.")
                continue
            if config['intent'] == '<Не выбрано>' or not config['intent']:
                QtWidgets.QMessageBox.about(self, "Ошибка", "Для фразы: <" + phrase + "> не выбрано намерение. Не могу сохранить.")
                continue
            #config['saved'] = True
            self.write_phrase_to_file(config)
        self.phrases_config = {}

    def clear_phrase(self, phrase):
        stripped_phrase = phrase
        if '{' in stripped_phrase:
            beg = 0
            while stripped_phrase.find('}', beg) != -1:
                stripped_phrase = stripped_phrase[:stripped_phrase.find('{', beg)+1] + stripped_phrase[stripped_phrase.find('}', beg):]
                after_index = stripped_phrase.find('}', beg)
                beg = after_index + 1
        return stripped_phrase

    def write_phrase_to_file(self, phrase_config):
        intents = self.domains[phrase_config['domain']]
        stripped_phrase = self.clear_phrase(phrase_config['end_phrase'])
        phrase_exists = False
        target_phrases = self.read_train_file(phrase_config['domain'], phrase_config['intent'])
        for intent in intents:
            phrases = self.read_train_file(phrase_config['domain'], intent)
            s_phrases = set()
            for p in phrases:
                sp = self.clear_phrase(p)
                s_phrases.add(sp)
            if stripped_phrase in s_phrases:
                log_item = QtWidgets.QListWidgetItem("Ошибка!!!   " + "Фраза: <" + stripped_phrase + "> уже есть в намерении: " + '"' + intent + '"')
                log_item.setBackground(QColor(colors[1]))
                self.save_log_list.addItem(log_item)
                #QtWidgets.QMessageBox.about(self, "Ошибка", "Фраза: <" + stripped_phrase + "> уже есть в намерении: " + '"' + intent + '"')
                phrase_exists = True
                break
        if not phrase_exists:
            #print('Wrote')
            log_item = QtWidgets.QListWidgetItem('OK.   Фраза записана в файл')
            log_item.setBackground(QColor(colors[0]))
            self.save_log_list.addItem(log_item)
            target_phrases.append(phrase_config['end_phrase'])
            self.update_train_file(phrase_config['domain'], phrase_config['intent'], target_phrases)
        #print(stripped_phrase)

        for syn_obj in phrase_config['synonims']:
            already_exists = False
            for ent_type, ent_type_obj in self.all_entities.items():
                for entity in ent_type_obj['entities']:
                    if syn_obj['synonim'] in entity['whitelist']:
                        already_exists = True
                        log_item = QtWidgets.QListWidgetItem("Ошибка!!!   " + 'Синоним "' + syn_obj['synonim'] + '"" уже существует в типе: <' + ent_type + '> сущности: <' + entity['cname'] + '>')
                        log_item.setBackground(QColor(colors[1]))
                        self.save_log_list.addItem(log_item)
                        #QtWidgets.QMessageBox.about(self, "Ошибка", 'Синоним "' + syn_obj['synonim'] + '"" уже существует в типе: <' + ent_type + '> сущности: <' + entity['cname'] + '>')
                        #print('Synonim exists for:', )
                        break
            if not already_exists:
                for ent_type, ent_type_obj in self.all_entities.items():
                    for entity in ent_type_obj['entities']:
                        if entity['cname'] == syn_obj['synonim_to']:
                            entity['whitelist'].append(syn_obj['synonim'])
                            #print('Added synonim')
                            break
                self.write_entity(syn_obj['ent_type'], self.all_entities[syn_obj['ent_type']])
                log_item = QtWidgets.QListWidgetItem('OK.   Синоним для ' + syn_obj['synonim_to'] + ' сохранен в файл')
                log_item.setBackground(QColor(colors[0]))
                self.save_log_list.addItem(log_item)

    def write_entity(self, ent_type, ent_object):
        with open(os.path.join(self.entities_root, ent_type, 'mapping.json'), 'w', encoding="utf-8") as f:
            f.write(json.dumps(ent_object, ensure_ascii=False))

    def get_domains_intents(self):
        domains = {}
        # r=root, d=directories, f = files
        #print(self.domains_path)
        for domain in os.listdir(self.domains_path):
            is_dir = os.path.isdir(os.path.join(self.domains_path, domain))
            if is_dir:
                domains[domain] = []
                for intent in os.listdir(os.path.join(self.domains_path, domain)):
                    is_dir_2 = os.path.isdir(os.path.join(self.domains_path, domain, intent))
                    if is_dir_2:
                        domains[domain].append(intent)
        return domains

    def load_entity_types_and_synonims(self):
        self.entities_root = os.path.join(self.path, 'entities')
        self.entities = []
        self.synonims = {}
        self.all_entities = {}
        ent_synonims = {}
        for entity in os.listdir(self.entities_root):
            is_dir = os.path.isdir(os.path.join(self.entities_root, entity))
            if is_dir:
                with open(os.path.join(self.entities_root, entity, 'mapping.json')) as f:
                    self.all_entities[entity] = json.loads(f.read())
                    ent_synonims[entity] = self.all_entities[entity]['entities']
                    self.entities.append(entity)
                self.synonims[entity] = []

        for ent_type, ents in ent_synonims.items():
            for ent in ents:
                for synonim in ent['whitelist']:
                    self.synonims[ent_type].append(synonim)

    def read_train_file(self, domain, intent):
        try:
            with open(os.path.join(self.domains_path, domain, intent, 'train.txt'), 'r') as f:
                phrases = f.readlines()
                phrases = [phr.strip() for phr in phrases]
        except:
            #print('File for:', domain, '/', intent, ' was not found. Creating a new one', sep='')
            with open(os.path.join(self.domains_path, domain, intent, 'train.txt'), 'w') as f:
                f.write('')
            phrases = []
        return phrases

    def update_train_file(self, domain, intent, new_phrases):
        random.shuffle(new_phrases)
        entire_text = '\n'.join(new_phrases)
        with open(os.path.join(self.domains_path, domain, intent, 'train.txt'), 'w') as f:
            f.write(entire_text)

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = Loader()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()

if __name__ == '__main__':
    main()