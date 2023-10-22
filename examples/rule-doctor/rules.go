package main

import (
	"log"
	"os"
	"path/filepath"

	"github.com/konveyor/analyzer-lsp/engine/labels"
	"github.com/konveyor/analyzer-lsp/output/v1/konveyor"
	"github.com/konveyor/analyzer-lsp/provider"
	"gopkg.in/yaml.v3"
)

type RuleFeatures struct {
	Description string
	Targets     []string
	Sources     []string
	Message     string
	Id          string
}

type Rule struct {
	Labels      []string `yaml:"labels,omitempty"`
	Id          string   `yaml:"ruleID,omitempty"`
	Message     string   `yaml:"message,omitempty"`
	Description string   `yaml:"description,omitempty"`
	Path        string
}

type RuleDiff struct {
	Path        string
	Id          string
	Description Diff
}

type Diff struct {
	From string
	To   string
}

func loadRules(path string) (map[string][]Rule, error) {
	rules := map[string][]Rule{}

	files, err := provider.FindFilesMatchingPattern(path, "*.yaml")
	if err != nil {
		return rules, nil
	}

	for idx := range files {
		file := files[idx]
		if filepath.Base(file) == "ruleset.yaml" {
			continue
		}
		if absPath, err := filepath.Abs(file); err == nil {
			file = absPath
		}
		if _, ok := rules[file]; !ok {
			rules[file] = []Rule{}
		}
		currentRules := []Rule{}
		content, err := os.ReadFile(file)
		if err != nil {
			log.Printf("failed to read file %s", file)
			continue
		}
		err = yaml.Unmarshal(content, &currentRules)
		if err != nil {
			log.Printf("failed to unmarshal file %s", file)
			continue
		}
		rules[file] = append(rules[file], currentRules...)
	}

	return rules, nil
}

func toRuleFeatures(rule Rule) RuleFeatures {
	ruleFeatures := RuleFeatures{
		Id:          rule.Id,
		Message:     rule.Message,
		Description: rule.Description,
		Sources:     []string{},
		Targets:     []string{},
	}

	for _, label := range rule.Labels {
		key, val, err := labels.ParseLabel(label)
		if err != nil {
			log.Println("failed parsing label", "label", label)
			continue
		}
		switch key {
		case konveyor.SourceTechnologyLabel:
			ruleFeatures.Sources = append(ruleFeatures.Sources, val)
		case konveyor.TargetTechnologyLabel:
			ruleFeatures.Targets = append(ruleFeatures.Targets, val)
		}
	}
	return ruleFeatures
}

func loadRuleFeatures(path string) (map[string][]RuleFeatures, error) {
	features := map[string][]RuleFeatures{}
	fileToRules, err := loadRules(path)
	if err != nil {
		return nil, err
	}
	for path, rules := range fileToRules {
		features[path] = []RuleFeatures{}
		for _, rule := range rules {
			features[path] = append(features[path], toRuleFeatures(rule))
		}
	}
	return features, nil
}
