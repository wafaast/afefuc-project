'''
Created on 19 Jun 2013

@author: Bartosz Alchimowicz, Michal Tomczyk, Mateusz Dembski
'''

from PyQt4 import QtGui, QtCore
import format.model
import re
import converter
#def identifier(parent):
#    return QtGui.QRegExpValidator(QtCore.QRegExp("[A-Z]+[A-Z_]*[0-9]*"), parent);

name_pattern = re.compile(r"[A-Z]+[a-z0-9_]*")

def _show(parent, errors):
    msg = ["The following errors were detected:"]

    for e in errors.items():
        msg.append("\n")
        msg.append("* %s" % e[0])
        msg.append(":\n")
        msg.append("\n".join(e[1]))

    QtGui.QMessageBox.about(parent, "Errors", "".join(msg))

def errorMessage(parent, error):
    msg = "The following error was detected:\n* " + error

    QtGui.QMessageBox.about(parent, "Errors", msg)

def _is_unique(item, itemsList):
    if itemsList.count(item) > 1:
        return False

    return True

def _count_field(test_item, items_list, field_name):

    count = 0;
    for item in items_list:
        if getattr(item, field_name) == getattr(test_item, field_name):
            count += 1

    return count

def _is_empty(text):
    if text is None: return False
    try:
        if len(text): return False
    except:
        return False

    return True

def _is_identifier(text):
    if text is None: return False
    if not re.match(r"[A-Z]+[A-Z_]*[0-9]*", text):
        return False

    return True

def _is_name(text):

    #import pdb
    #pdb.set_trace()

    if not name_pattern.match(text):
#     if not re.match(r"[A-Z]+[a-z0-9_]*", text):
        return False

    return True

def _is_title(text):

    if text == []: return False
    return True

def priority(project, item, edit):
    errors = {}

    if edit:
        upper = 0
    else:
        upper = 1

    if(_is_name(item.name) == False):
        errors['Name'] = {"Name should start with uppercase"}

    if _is_empty(item.name):
        errors['Name'] = {"This field cannot be empty"}

    if _count_field(item, project.ucspec.priorities, "name") > upper:
        errors['Name'] = {"The following name is not unique"}

    return errors

def goal_level(project, item, edit):
    errors = {}

    if edit:
        upper = 0
    else:
        upper = 1

    if(_is_name(item.name) == False):
        errors['Name'] = {"Name should start with uppercase"}

    if _is_empty(item.name):
        errors['Name'] = {"This field cannot be empty"}

    if _count_field(item, project.ucspec.goal_levels, "name") > upper:
        errors['Name'] = {"The following name is not unique"}

    return errors

def business_object(project, item, edit):
    errors = {}

    if edit:
        upper = 0
    else:
        upper = 1



    if(_is_title(item.name) == False):
        errors['Name'] = {"Name cannot be empty."}

    if _is_empty(item.name):
        errors['Name'] = {"This field cannot be empty"}

    if _count_field(item, project.business_objects, "name") > upper:
        errors['Name'] = {"The following name is not unique"}

    if(_is_identifier(item.identifier) == False):
        errors['ID'] = {"Identifier should start with uppercase"}
    elif _is_empty(item.identifier):
        errors['ID'] = {"This field cannot be empty"}
    elif _count_field(item, project.business_objects, "identifier") > upper:
        errors['ID'] = {"The following identifier is not unique"}

    for a in item.attributes:
        if(_is_name(a.name) == False):
            errors['Attribute name'] = {"Attribute has not a valid name"}

        if(_is_empty(a.name) == True):
            errors['Attribute description'] = {"Attribute descripton couldn't be empty"}

    return errors

def business_rule(project, item, edit):
    errors = {}

    if edit:
        upper = 0
    else:
        upper = 1

    if(_is_identifier(item.identifier) == False):
        errors['ID'] = {"Identifier should start with uppercase"}
    elif _is_empty(item.identifier):
        errors['ID'] = {"This field cannot be empty"}
    elif _count_field(item, project.business_rules, "identifier") > upper:
        errors['ID'] = {"The following identifier is not unique"}

    return errors

def actor(project, item, edit):
    errors = {}

    if edit:
        upper = 0
    else:
        upper = 1

    if(_is_name(item.name) == False):
        errors['Name'] = {"Name should start with uppercase"}

    if _is_empty(item.name):
        errors['Name'] = {"This field cannot be empty"}

    if(_is_identifier(item.identifier) == False):
        errors['ID'] = {"Identifier should start with uppercase"}
    elif _is_empty(item.identifier):
        errors['ID'] = {"This field cannot be empty"}
    elif _count_field(item, project.actors, "identifier") > upper:
        errors['ID'] = {"The following identifier is not unique"}

    if _count_field(item, project.actors, "name") > upper:
        errors['Name'] = {"The following name is not unique"}

    return errors

def usecase(project, item, edit, form):
    errors = {}
    #import pdb
    #pdb.set_trace()

    if edit:
        upper = 0
    else:
        upper = 1

#     # priority
#     index = form.priorityComboBox.currentIndex()
#     priority = form.priorityComboBox.itemData(index).toPyObject()
#
#     try:
#         item.priority = priority.get_ref()
#     except:
#         errors['Priority'] = {"Priority must be specified"}
#
#     # goal
#     index = form.goalLevelComboBox.currentIndex()
#     priority = form.goalLevelComboBox.itemData(index).toPyObject()
#
#     try:
#         item.goal_level = priority.get_ref()
#     except:
#         errors['Goal level'] = {"Goal level must be specified"}
#
#     # remarks
#     try:
#         item.remarks = converter.textToItems(
# 			project.afefuc['project'],
# 			unicode(form.remarksTextEdit.toPlainText().toUtf8(), "utf-8")
# 		)
#     except:
#         errors['Remarks'] = {"Invalid reference in remarks"}
#
#     # summary
#     try:
#         item.summary = converter.textToItems(
# 			project.afefuc['project'],
# 			unicode(form.summaryTextEdit.toPlainText().toUtf8(), "utf-8")
# 		)
#     except:
#         errors['Summary'] = {"Invalid reference in summary"}

    # title
    if(_is_title(item.title) == False):
        errors['Name'] = {"Title cannot be empty."}

    # id
    if _is_empty(item.identifier):
        errors['ID'] = {"This field cannot be empty"}
    elif(_is_identifier(item.identifier) == False):
        errors['ID'] = {"Identifier should start with uppercase"}
    elif _count_field(item, project.ucspec.usecases, 'identifier') > upper:
        errors['ID'] = {"Identifier should be unique"}

    # there should be at least one main actor and one other
    if item.scenario.items:
        if len(item.main_actors) == 0:
            errors['main_actors'] = {"There should be at least one main actor"}
        if len(item.other_actors) == 0:
            errors['main_actors'] = {"There should be at least one other actor"}

    scenario_errors = scenario(project, item.scenario, edit)
    errors.update(scenario_errors)

    return errors

def scenario(project, item, edit):
    errors = {}

    if edit:
        upper = 0
    else:
        upper = 1

    # step in uc cannot be empty (step.items.len > 0)
    for step in item.items:
        if len(step.items) == 0:
            errors['Scenario'] = {"Step in scenario cannot be empty."}
        else:
            commands = 0
            for sitem in step.items:
                if isinstance(sitem, format.model.EoUCCommand) or isinstance(sitem, format.model.GoToCommand):
                    commands = commands + 1
            if commands > 1:
                errors['Step commands'] = {"There can be at most one @eouc or @goto command in step"}
        for event in step.events:
            scenario_errors = scenario(project, event.scenario, edit)
            errors.update(scenario_errors)


    if len(item.items) > 0:
        if len(item.items[-1].items) > 0:
            #import pdb
            #pdb.set_trace()
            ok=False
            for sitem in item.items[-1].items:
                if isinstance(sitem, format.model.Command):
                    ok=True
            if ok==False:
                errors['Scenario'] = {"Scenario should end with @eouc or @goto"}
    return errors


def glossary(project, item, edit):
    errors = {}

    if edit:
        upper = 0
    else:
        upper = 1

    if(_is_name(item.name) == False):
        errors['Name'] = {"Name should start with uppercase"}

    if _is_empty(item.name):
        errors['Name'] = {"This field cannot be empty"}

    if _count_field(item, project.glossary, 'name') > upper:
        errors['Name'] = {"Name should be unique"}

    if _count_field(item, project.glossary, 'definition') > upper:
        errors['Definition'] = {"Definition should be unique"};


    return errors